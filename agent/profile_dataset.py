#!/usr/bin/env python3
"""Build a compact dataset_profile.json from archived ROBERT outputs.

This module is read-only with respect to ROBERT core code. It only reads files from
an archived run and writes one companion artifact: dataset_profile.json.
"""

from __future__ import annotations

import ast
import json
import re
import shlex
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd


def _safe_float(value: Any) -> Optional[float]:
    try:
        if value is None:
            return None
        return float(value)
    except Exception:
        return None


def _safe_int(value: Any) -> Optional[int]:
    try:
        if value is None:
            return None
        return int(value)
    except Exception:
        return None


def _parse_ignore_list(raw_value: Any) -> List[str]:
    if isinstance(raw_value, list):
        return [str(x) for x in raw_value]

    if raw_value is None:
        return []

    text = str(raw_value).strip()
    if not text:
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except Exception:
        pass

    if text.startswith("[") and text.endswith("]"):
        text = text[1:-1]

    parts = [p.strip().strip("\"'") for p in text.split(",")]
    return [p for p in parts if p]


def _parse_command_csv_name(lines: List[str]) -> Optional[str]:
    command_line = None
    for line in lines:
        if "Command line used in ROBERT:" in line:
            command_line = line.split("Command line used in ROBERT:", 1)[1].strip()
            break
    if not command_line:
        return None

    try:
        tokens = shlex.split(command_line)
    except Exception:
        return None

    for idx, token in enumerate(tokens):
        if token == "--csv_name" and idx + 1 < len(tokens):
            return tokens[idx + 1]
    return None


def _parse_curate_dat(dat_path: Path) -> Dict[str, Any]:
    info: Dict[str, Any] = {
        "log_datapoints": None,
        "log_accepted_descriptors": None,
        "constant_columns": [],
        "non_numeric_descriptors": [],
        "highly_correlated_pairs": [],
        "source_csv_path_from_command": None,
        "warnings": [],
    }

    if not dat_path.exists():
        info["warnings"].append(f"Missing CURATE dat file: {dat_path}")
        return info

    lines = dat_path.read_text(encoding="utf-8", errors="replace").splitlines()
    info["source_csv_path_from_command"] = _parse_command_csv_name(lines)

    in_categorical_initial = False
    in_generated = False

    for line in lines:
        stripped = line.strip()

        m_rows = re.search(r"-\s+(\d+)\s+datapoints", stripped)
        if m_rows:
            info["log_datapoints"] = _safe_int(m_rows.group(1))

        m_desc = re.search(r"-\s+(\d+)\s+accepted descriptors", stripped)
        if m_desc:
            info["log_accepted_descriptors"] = _safe_int(m_desc.group(1))

        m_const = re.search(r"-\s+(.+?):\s+all the values are the same", stripped)
        if m_const:
            info["constant_columns"].append(m_const.group(1).strip())

        m_corr = re.search(
            r"-\s+(.+?)\s+removed\s+\(R2\s*=\s*([\d.]+)\s+with\s+(.+?)\)",
            stripped,
        )
        if m_corr:
            info["highly_correlated_pairs"].append(
                {
                    "removed": m_corr.group(1).strip(),
                    "correlated_with": m_corr.group(3).strip(),
                    "r2": _safe_float(m_corr.group(2)),
                }
            )

        if stripped.startswith("Initial descriptors:"):
            in_categorical_initial = True
            in_generated = False
            continue

        if stripped.startswith("Generated descriptors:"):
            in_generated = True
            in_categorical_initial = False
            continue

        if in_generated and stripped.startswith("-"):
            continue

        if in_categorical_initial:
            if stripped.startswith("-"):
                info["non_numeric_descriptors"].append(stripped.lstrip("-").strip())
            elif stripped == "":
                in_categorical_initial = False

    return info


def _load_curate_options(options_path: Path) -> Dict[str, Any]:
    defaults: Dict[str, Any] = {
        "target": None,
        "names": None,
        "ignored": [],
        "curated_csv_path_from_options": None,
        "warnings": [],
    }

    if not options_path.exists():
        defaults["warnings"].append(f"Missing CURATE options file: {options_path}")
        return defaults

    try:
        df = pd.read_csv(options_path)
    except Exception as exc:
        defaults["warnings"].append(f"Failed to read CURATE options file: {exc}")
        return defaults

    if df.empty:
        defaults["warnings"].append("CURATE options file is empty.")
        return defaults

    row = df.iloc[0]
    defaults["target"] = None if pd.isna(row.get("y")) else str(row.get("y"))
    defaults["names"] = None if pd.isna(row.get("names")) else str(row.get("names"))
    defaults["ignored"] = _parse_ignore_list(row.get("ignore"))
    csv_name = row.get("csv_name")
    defaults["curated_csv_path_from_options"] = None if pd.isna(csv_name) else str(csv_name)
    return defaults


def _find_curated_csv(curate_dir: Path, target_col: Optional[str]) -> Optional[Path]:
    csv_candidates = [p for p in curate_dir.glob("*_CURATE.csv") if p.is_file()]
    if not csv_candidates:
        return None

    if target_col:
        for path in sorted(csv_candidates):
            try:
                cols = list(pd.read_csv(path, nrows=0).columns)
                if target_col in cols:
                    return path
            except Exception:
                continue

    return sorted(csv_candidates)[0]


def _pick_source_csv(
    command_csv_path: Optional[str],
    curated_csv_path: Optional[Path],
    warnings: List[str],
) -> Optional[Path]:
    if command_csv_path:
        p = Path(command_csv_path)
        if p.exists() and p.is_file():
            return p
        warnings.append(f"Original CSV from CURATE command not found: {command_csv_path}")

    if curated_csv_path and curated_csv_path.exists():
        warnings.append("Falling back to curated CSV because original input CSV was unavailable.")
        return curated_csv_path

    warnings.append("No readable source CSV found.")
    return None


def _infer_problem_type(target_series: pd.Series) -> str:
    if target_series.dtype == "object":
        return "clas"

    unique_count = int(target_series.nunique(dropna=True))
    if unique_count == 2:
        return "clas"
    return "reg"


def _safe_numeric_series(series: pd.Series) -> Optional[pd.Series]:
    converted = pd.to_numeric(series, errors="coerce")
    if converted.notna().sum() < 3:
        return None
    return converted


def _top_descriptor_target_correlations(
    curated_df: pd.DataFrame,
    target_col: Optional[str],
    ignored: List[str],
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    if not target_col or target_col not in curated_df.columns:
        return []

    target = _safe_numeric_series(curated_df[target_col])
    if target is None:
        return []

    results: List[Dict[str, Any]] = []
    for col in curated_df.columns:
        if col == target_col or col in ignored:
            continue

        descriptor = _safe_numeric_series(curated_df[col])
        if descriptor is None:
            continue

        corr = descriptor.corr(target)
        if pd.isna(corr):
            continue

        r2 = float(corr * corr)
        results.append({"descriptor": col, "r2_with_target": round(r2, 6)})

    results.sort(key=lambda item: item["r2_with_target"], reverse=True)
    return results[:top_n]


def profile_dataset(
    run_folder: str | Path,
    write_json: bool = True,
    include_smiles_summary: bool = False,
) -> Dict[str, Any]:
    """Generate one dataset profile dict and optionally write dataset_profile.json.

    Args:
        run_folder: Path to one run archive directory.
        write_json: If True, write dataset_profile.json in run_folder.
        include_smiles_summary: Placeholder flag; currently deferred to keep scope small.
    """

    run_path = Path(run_folder).resolve()
    curate_dir = run_path / "outputs" / "CURATE"
    dat_path = curate_dir / "CURATE_data.dat"
    options_path = curate_dir / "CURATE_options.csv"

    warnings: List[str] = []

    dat_info = _parse_curate_dat(dat_path)
    warnings.extend(dat_info.get("warnings", []))

    options_info = _load_curate_options(options_path)
    warnings.extend(options_info.get("warnings", []))

    target_col = options_info.get("target")
    names_col = options_info.get("names")
    ignored_cols = options_info.get("ignored", [])

    curated_csv_path = _find_curated_csv(curate_dir, target_col)
    source_csv_path = _pick_source_csv(
        dat_info.get("source_csv_path_from_command"),
        curated_csv_path,
        warnings,
    )

    if source_csv_path is None:
        profile = {
            "version": "1.0",
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_csv": None,
            "source_csv_path": None,
            "row_count": None,
            "column_count": None,
            "column_headings": [],
            "column_roles": {
                "target": target_col,
                "names": names_col,
                "smiles": None,
                "ignored": ignored_cols,
                "discarded": [],
                "candidate_descriptors": [],
            },
            "candidate_descriptor_count": dat_info.get("log_accepted_descriptors"),
            "missingness": {},
            "target_summary": None,
            "target_imbalance": None,
            "constant_columns": dat_info.get("constant_columns", []),
            "near_constant_columns": [],
            "non_numeric_descriptors": dat_info.get("non_numeric_descriptors", []),
            "highly_correlated_pairs": dat_info.get("highly_correlated_pairs", []),
            "top_descriptor_target_correlations": [],
            "smiles_summary": None,
            "parser_warnings": warnings,
        }
        if write_json:
            out_path = run_path / "dataset_profile.json"
            out_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")
        return profile

    df = pd.read_csv(source_csv_path)
    row_count = int(len(df))
    column_headings = [str(c) for c in df.columns]
    column_count = int(len(column_headings))

    smiles_col = None
    for col in column_headings:
        if str(col).lower().startswith("smiles"):
            smiles_col = str(col)
            break

    excluded = set(ignored_cols)
    if target_col:
        excluded.add(target_col)
    if names_col:
        excluded.add(names_col)
    candidate_descriptors = [c for c in column_headings if c not in excluded]

    missingness = {col: int(df[col].isna().sum()) for col in column_headings}

    target_summary = None
    target_imbalance = None
    if target_col and target_col in df.columns:
        y = df[target_col]
        pred_type = _infer_problem_type(y)

        if pred_type == "clas":
            class_counts = y.value_counts(dropna=False).to_dict()
            class_counts_str = {str(k): int(v) for k, v in class_counts.items()}
            counts = list(class_counts_str.values())
            if counts and min(counts) > 0:
                class_ratio = round(max(counts) / min(counts), 6)
                minority_pct = round((min(counts) / sum(counts)) * 100.0, 3)
            else:
                class_ratio = None
                minority_pct = None

            target_summary = {
                "type": "clas",
                "min": None,
                "max": None,
                "mean": None,
                "median": None,
                "std": None,
                "range": None,
                "class_counts": class_counts_str,
            }
            target_imbalance = {
                "class_ratio": class_ratio,
                "minority_class_pct": minority_pct,
            }
        else:
            y_num = pd.to_numeric(y, errors="coerce")
            target_summary = {
                "type": "reg",
                "min": _safe_float(y_num.min()),
                "max": _safe_float(y_num.max()),
                "mean": _safe_float(y_num.mean()),
                "median": _safe_float(y_num.median()),
                "std": _safe_float(y_num.std()),
                "range": _safe_float(y_num.max() - y_num.min()) if y_num.notna().any() else None,
                "class_counts": None,
            }
            target_imbalance = {
                "class_ratio": None,
                "minority_class_pct": None,
            }

    top_corr = []
    if curated_csv_path and curated_csv_path.exists():
        curated_df = pd.read_csv(curated_csv_path)
        top_corr = _top_descriptor_target_correlations(curated_df, target_col, ignored_cols)
    else:
        warnings.append("Could not compute descriptor-target correlations; curated CSV missing.")

    smiles_summary = None
    if include_smiles_summary and smiles_col:
        warnings.append("SMILES summary requested but deferred in this iteration.")

    profile = {
        "version": "1.0",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_csv": source_csv_path.name,
        "source_csv_path": str(source_csv_path),
        "row_count": row_count,
        "column_count": column_count,
        "column_headings": column_headings,
        "column_roles": {
            "target": target_col,
            "names": names_col,
            "smiles": smiles_col,
            "ignored": ignored_cols,
            "discarded": [],
            "candidate_descriptors": candidate_descriptors,
        },
        "candidate_descriptor_count": dat_info.get("log_accepted_descriptors")
        if dat_info.get("log_accepted_descriptors") is not None
        else len(candidate_descriptors),
        "missingness": missingness,
        "target_summary": target_summary,
        "target_imbalance": target_imbalance,
        "constant_columns": dat_info.get("constant_columns", []),
        "near_constant_columns": [],
        "non_numeric_descriptors": dat_info.get("non_numeric_descriptors", []),
        "highly_correlated_pairs": dat_info.get("highly_correlated_pairs", []),
        "top_descriptor_target_correlations": top_corr,
        "smiles_summary": smiles_summary,
        "parser_warnings": warnings,
    }

    if write_json:
        out_path = run_path / "dataset_profile.json"
        out_path.write_text(json.dumps(profile, indent=2, ensure_ascii=False), encoding="utf-8")

    return profile
