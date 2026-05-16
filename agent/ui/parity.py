"""Parity verification helpers for UI safety gating.

This module deterministically checks whether extracted run_context values
match ROBERT source evidence files in outputs/PREDICT and outputs/VERIFY.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


def _safe_float(value: Optional[str]) -> Optional[float]:
    if value is None:
        return None
    try:
        return float(value.strip())
    except (AttributeError, ValueError):
        return None


def _safe_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value.strip())
    except (AttributeError, ValueError):
        return None


def _split_into_blocks(lines: List[str], no_pfi_marker: str, pfi_marker: str) -> Dict[str, List[str]]:
    blocks = {"no_pfi": [], "pfi": []}
    current: Optional[str] = None
    for line in lines:
        if no_pfi_marker in line:
            current = "no_pfi"
        elif pfi_marker in line:
            current = "pfi"
        if current is not None:
            blocks[current].append(line)
    return blocks


def _extract_predict_expected(predict_dat_path: Path) -> Dict[str, Dict[str, Any]]:
    with open(predict_dat_path, "r") as f:
        lines = f.readlines()

    blocks = _split_into_blocks(
        lines,
        "Starting model with all variables (No PFI)",
        "Starting model with PFI filter",
    )

    expected: Dict[str, Dict[str, Any]] = {}
    for variant in ["no_pfi", "pfi"]:
        text = "".join(blocks[variant])
        expected[variant] = {}

        m = re.search(r"Training points:\s+(\d+)", text)
        if m:
            expected[variant]["n_train"] = _safe_int(m.group(1))

        m = re.search(r"Test points:\s+(\d+)", text)
        if m:
            expected[variant]["n_test"] = _safe_int(m.group(1))

        m = re.search(r"Number of descriptors\s*=\s*(\d+)", text)
        if m:
            expected[variant]["n_descriptors"] = _safe_int(m.group(1))

        m = re.search(r"(\d+)x\s+(\d+)-fold CV\s*:\s+R2\s*=\s*([\d.eE+\-]+)", text)
        if m:
            expected[variant]["r2_cv"] = _safe_float(m.group(3))

        m = re.search(r"Test\s*:\s+R2\s*=\s*([\d.eE+\-]+)", text)
        if m:
            expected[variant]["r2_test"] = _safe_float(m.group(1))

        m = re.search(r"(\d+)x\s+(\d+)-fold CV\s*:.*?RMSE\s*=\s*([\d.eE+\-]+)", text)
        if m:
            expected[variant]["rmse_cv"] = _safe_float(m.group(3))

        m = re.search(r"Test\s*:.*?RMSE\s*=\s*([\d.eE+\-]+)", text)
        if m:
            expected[variant]["rmse_test"] = _safe_float(m.group(1))

        m = re.search(r"(\d+)x\s+(\d+)-fold CV\s*:.*?MCC\s*=\s*([\d.eE+\-]+)", text)
        if m:
            expected[variant]["mcc_cv"] = _safe_float(m.group(3))

        m = re.search(r"Test\s*:.*?MCC\s*=\s*([\d.eE+\-]+)", text)
        if m:
            expected[variant]["mcc_test"] = _safe_float(m.group(1))

    return expected


def _extract_verify_expected(verify_dat_path: Path) -> Dict[str, Dict[str, Any]]:
    with open(verify_dat_path, "r") as f:
        lines = f.readlines()

    blocks = _split_into_blocks(
        lines,
        "Starting model with all variables (No PFI)",
        "Starting model with PFI filter",
    )

    expected: Dict[str, Dict[str, Any]] = {}
    for variant in ["no_pfi", "pfi"]:
        text = "".join(blocks[variant])
        expected[variant] = {}

        matches = re.compile(r"[ox\-]\s+(y_mean|y_shuffle|onehot):\s+(PASSED|UNCLEAR|FAILED)").findall(text)
        if matches:
            expected[variant]["test_results"] = [f"{test}: {verdict}" for test, verdict in matches]
            expected[variant]["passed_tests"] = sum(1 for _, v in matches if v == "PASSED")
            expected[variant]["unclear_tests"] = sum(1 for _, v in matches if v == "UNCLEAR")
            expected[variant]["failed_tests"] = sum(1 for _, v in matches if v == "FAILED")
            expected[variant]["flawed_mod_score"] = (
                expected[variant]["unclear_tests"] * (-1) + expected[variant]["failed_tests"] * (-2)
            )

        m = re.search(r"Sorted\s+CV\s*:.*?RMSE\s*=\s*(\[[^\]]+\])", text, re.DOTALL)
        if m:
            try:
                expected[variant]["sorted_cv_rmse"] = json.loads(m.group(1))
            except Exception:
                expected[variant]["sorted_cv_rmse"] = None

        m = re.search(r"Sorted\s+CV\s*:.*?R2\s*=\s*(\[[^\]]+\])", text, re.DOTALL)
        if m:
            try:
                expected[variant]["sorted_cv_r2"] = json.loads(m.group(1))
            except Exception:
                expected[variant]["sorted_cv_r2"] = None

        m = re.search(r"Sorted\s+CV\s*:.*?MCC\s*=\s*(\[[^\]]+\])", text, re.DOTALL)
        if m:
            try:
                expected[variant]["sorted_cv_mcc"] = json.loads(m.group(1))
            except Exception:
                expected[variant]["sorted_cv_mcc"] = None

    return expected


def _check_predict_parity(
    run_context: Dict[str, Any], expected: Dict[str, Dict[str, Any]], pred_type: str
) -> Tuple[List[str], List[str]]:
    gaps: List[str] = []
    failures: List[str] = []

    for variant in ["no_pfi", "pfi"]:
        got = run_context.get("predict", {}).get(variant, {})
        exp = expected.get(variant, {})

        for field in ["n_train", "n_test", "n_descriptors"]:
            if field in exp and exp[field] is not None and got.get(field) != exp[field]:
                failures.append(f"predict.{variant}.{field}: got {got.get(field)}, expected {exp[field]}")

        metric_fields = ["r2_cv", "r2_test", "rmse_cv", "rmse_test"] if pred_type == "reg" else ["mcc_cv", "mcc_test"]
        for field in metric_fields:
            if field not in exp or exp[field] is None:
                continue
            got_val = got.get(field)
            if got_val is None:
                gaps.append(f"predict.{variant}.{field}")
                continue
            if abs(got_val - exp[field]) > 1e-5:
                failures.append(f"predict.{variant}.{field}: got {got_val}, expected {exp[field]}")

    return gaps, failures


def _check_verify_parity(run_context: Dict[str, Any], expected: Dict[str, Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    gaps: List[str] = []
    failures: List[str] = []

    for variant in ["no_pfi", "pfi"]:
        got = run_context.get("verify", {}).get(variant, {})
        exp = expected.get(variant, {})

        for field in ["passed_tests", "unclear_tests", "failed_tests", "flawed_mod_score"]:
            if field in exp and exp[field] is not None and got.get(field) != exp[field]:
                failures.append(f"verify.{variant}.{field}: got {got.get(field)}, expected {exp[field]}")

        if exp.get("test_results") and got.get("test_results") != exp["test_results"]:
            failures.append(f"verify.{variant}.test_results: mismatch")

        for field in ["sorted_cv_rmse", "sorted_cv_r2", "sorted_cv_mcc"]:
            if field not in exp or exp[field] is None:
                continue
            got_val = got.get(field)
            if got_val is None:
                gaps.append(f"verify.{variant}.{field}")
            elif got_val != exp[field]:
                failures.append(f"verify.{variant}.{field}: mismatch")

    return gaps, failures


def check_parity(run_context: Dict[str, Any], run_root: Path) -> Dict[str, Any]:
    """Return parity verification result for a run.

    Result keys: run_id, pred_type, parity_status, gaps, failures, messages
    """
    run_id = str(run_context.get("run_id", "unknown"))
    pred_type = run_context.get("pred_type")
    available = run_context.get("available", {}) if isinstance(run_context, dict) else {}

    outputs_root = run_root / "outputs"
    predict_dat = outputs_root / "PREDICT" / "PREDICT_data.dat"
    verify_dat = outputs_root / "VERIFY" / "VERIFY_data.dat"

    gaps: List[str] = []
    failures: List[str] = []
    messages: List[str] = []
    has_unavailable_modules = False

    if available.get("predict"):
        if predict_dat.exists():
            expected_predict = _extract_predict_expected(predict_dat)
            pg, pf = _check_predict_parity(run_context, expected_predict, str(pred_type or ""))
            gaps.extend(pg)
            failures.extend(pf)
            messages.append("PREDICT evidence parity checked")
        else:
            gaps.append("predict_data.dat")
            messages.append("PREDICT marked available but PREDICT_data.dat is missing")
    else:
        has_unavailable_modules = True
        gaps.append("predict_unavailable")
        messages.append("PREDICT module unavailable for this run")

    if available.get("verify"):
        if verify_dat.exists():
            expected_verify = _extract_verify_expected(verify_dat)
            vg, vf = _check_verify_parity(run_context, expected_verify)
            gaps.extend(vg)
            failures.extend(vf)
            messages.append("VERIFY evidence parity checked")
        else:
            gaps.append("verify_data.dat")
            messages.append("VERIFY marked available but VERIFY_data.dat is missing")
    else:
        has_unavailable_modules = True
        gaps.append("verify_unavailable")
        messages.append("VERIFY module unavailable for this run")

    for optional_module in ["curate", "generate"]:
        if optional_module in available and not available.get(optional_module):
            has_unavailable_modules = True
            gaps.append(f"{optional_module}_unavailable")
            messages.append(f"{optional_module.upper()} module unavailable for this run")

    if failures:
        status = "fail"
        messages.insert(0, "Parity failed: extracted values do not match source evidence")
    elif gaps:
        critical_gaps = [g for g in gaps if "data.dat" in g or "n_" in g or "passed_tests" in g]
        if critical_gaps:
            status = "fail"
            messages.insert(0, "Parity failed: critical evidence fields are missing")
        else:
            status = "incomplete"
            messages.insert(0, "Parity incomplete: optional evidence fields are missing")
    elif has_unavailable_modules:
        status = "incomplete"
        messages.insert(0, "Parity incomplete: one or more ROBERT modules are unavailable")
    else:
        status = "pass"
        messages.insert(0, "Parity passed: extraction matches source evidence")

    return {
        "run_id": run_id,
        "pred_type": pred_type,
        "parity_status": status,
        "gaps": gaps,
        "failures": failures,
        "messages": messages,
    }
