#!/usr/bin/env python3
"""Normalize archived ROBERT run assets and rebuild LLM bundles.

This utility enforces deterministic report PDF names per run and rebuilds
llm_run_bundle from run_context.json + llm_evidence.json.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Summary:
    updated: list[str]
    skipped: list[str]
    warnings: list[str]


def sanitize_tag(text: str) -> str:
    cleaned = []
    for ch in text:
        if ch.isalnum() or ch in {"-", "_"}:
            cleaned.append(ch)
        else:
            cleaned.append("_")
    out = "".join(cleaned).strip("_")
    return out or "dataset"


def safe_read_json(path: Path, summary: Summary, run_name: str) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        summary.warnings.append(f"{run_name}: could not read {path.name} ({exc})")
        return None


def infer_dataset_tag(run_name: str, run_context: dict | None, manifest: dict | None) -> tuple[str, str]:
    if "__" in run_name:
        run_timestamp, fallback_dataset = run_name.split("__", 1)
    else:
        run_timestamp, fallback_dataset = datetime.now().strftime("%Y%m%d_%H%M%S"), run_name

    dataset_csv = None
    if run_context:
        dataset_csv = run_context.get("dataset_csv")
    elif manifest:
        dataset_csv = manifest.get("dataset_csv")

    if dataset_csv:
        dataset_tag = sanitize_tag(Path(dataset_csv).stem)
    else:
        dataset_tag = sanitize_tag(fallback_dataset)

    return run_timestamp, dataset_tag


def prepare_source_candidates(
    run_dir: Path,
    report_assets: Path,
    project_root: Path,
    summary: Summary,
    run_name: str,
) -> list[tuple[Path, str]]:
    """Return list of (existing_source_path, source_label_for_metadata)."""
    pdfs = [p for p in report_assets.glob("*.pdf") if p.is_file()]
    if pdfs:
        # Copy sources into a temporary folder to avoid delete-then-copy races.
        temp_dir = run_dir / ".tmp_report_sources"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        temp_dir.mkdir(parents=True, exist_ok=True)

        prepared: list[tuple[Path, str]] = []
        for src in pdfs:
            temp_src = temp_dir / src.name
            try:
                shutil.copy2(src, temp_src)
                prepared.append((temp_src, str(src.resolve())))
            except Exception as exc:  # noqa: BLE001
                summary.warnings.append(
                    f"{run_name}: failed staging report source {src.name} ({exc})"
                )
        return prepared

    root_pdf = project_root / "ROBERT_report.pdf"
    if root_pdf.exists():
        return [(root_pdf, str(root_pdf.resolve()))]

    return []


def rewrite_report_assets(
    run_dir: Path,
    report_assets: Path,
    source_candidates: list[tuple[Path, str]],
    dataset_tag: str,
    run_timestamp: str,
    summary: Summary,
    run_name: str,
) -> list[dict]:
    for old in report_assets.glob("*.pdf"):
        try:
            old.unlink()
        except Exception as exc:  # noqa: BLE001
            summary.warnings.append(f"{run_name}: failed to remove {old.name} ({exc})")

    linked_reports: list[dict] = []
    for idx, (src, src_label) in enumerate(source_candidates, start=1):
        base = f"{dataset_tag}__{run_timestamp}__ROBERT_report"
        suffix = "" if idx == 1 else f"__{idx}"
        dest = report_assets / f"{base}{suffix}.pdf"
        try:
            shutil.copy2(src, dest)
            linked_reports.append(
                {
                    "name": dest.name,
                    "path": str(dest.resolve()),
                    "source_path": src_label,
                    "dataset_tag": dataset_tag,
                    "run_timestamp": run_timestamp,
                }
            )
        except Exception as exc:  # noqa: BLE001
            summary.warnings.append(f"{run_name}: failed to copy report from {src} ({exc})")

    temp_dir = run_dir / ".tmp_report_sources"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    return linked_reports


def write_json(path: Path, data: dict, summary: Summary, run_name: str) -> bool:
    try:
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True
    except Exception as exc:  # noqa: BLE001
        summary.warnings.append(f"{run_name}: failed writing {path.name} ({exc})")
        return False


def rebuild_bundle(run_dir: Path, linked_reports: list[dict], summary: Summary, run_name: str) -> bool:
    run_context_path = run_dir / "run_context.json"
    llm_evidence_path = run_dir / "llm_evidence.json"
    bundle_dir = run_dir / "llm_run_bundle"
    reports_dir = bundle_dir / "report_assets"

    try:
        if bundle_dir.exists():
            shutil.rmtree(bundle_dir)
        reports_dir.mkdir(parents=True, exist_ok=True)
    except Exception as exc:  # noqa: BLE001
        summary.warnings.append(f"{run_name}: failed resetting llm_run_bundle ({exc})")
        return False

    try:
        shutil.copy2(run_context_path, bundle_dir / "run_context.json")
        shutil.copy2(llm_evidence_path, bundle_dir / "llm_evidence.json")

        bundled_reports = []
        for item in linked_reports:
            src = Path(item["path"])
            dest = reports_dir / src.name
            shutil.copy2(src, dest)
            bundled_reports.append(
                {
                    "name": dest.name,
                    "path": str(dest.resolve()),
                    "source_path": str(src.resolve()),
                }
            )

        bundle_index = {
            "schema_version": "1.0",
            "bundle_created_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "bundle_dir": str(bundle_dir.resolve()),
            "files": {
                "run_context": str((bundle_dir / "run_context.json").resolve()),
                "llm_evidence": str((bundle_dir / "llm_evidence.json").resolve()),
                "report_assets": bundled_reports,
            },
            "routing": {
                "ui_pdf_view_source": "report_assets",
                "llm_prompt_source": "llm_evidence.json",
                "note": "LLM should use extracted evidence only, not PDF text.",
            },
        }
        write_json(bundle_dir / "bundle_index.json", bundle_index, summary, run_name)
        return True
    except Exception as exc:  # noqa: BLE001
        summary.warnings.append(f"{run_name}: failed rebuilding llm_run_bundle ({exc})")
        return False


def normalize_runs() -> Summary:
    root = Path("agent/run_archive")
    project_root = Path(".").resolve()

    summary = Summary(updated=[], skipped=[], warnings=[])

    if not root.exists():
        summary.warnings.append("agent/run_archive does not exist")
        return summary

    for run_dir in sorted([p for p in root.iterdir() if p.is_dir()]):
        run_name = run_dir.name
        run_context_path = run_dir / "run_context.json"
        llm_evidence_path = run_dir / "llm_evidence.json"
        manifest_path = run_dir / "run_manifest.json"

        if not (run_context_path.exists() and llm_evidence_path.exists()):
            summary.skipped.append(f"{run_name} (missing run_context.json or llm_evidence.json)")
            continue

        run_context = safe_read_json(run_context_path, summary, run_name)
        llm_evidence = safe_read_json(llm_evidence_path, summary, run_name)
        manifest = safe_read_json(manifest_path, summary, run_name) if manifest_path.exists() else None

        if run_context is None or llm_evidence is None:
            summary.skipped.append(f"{run_name} (failed to read required JSON)")
            continue

        run_timestamp, dataset_tag = infer_dataset_tag(run_name, run_context, manifest)

        report_assets = run_dir / "report_assets"
        report_assets.mkdir(parents=True, exist_ok=True)

        source_candidates = prepare_source_candidates(
            run_dir=run_dir,
            report_assets=report_assets,
            project_root=project_root,
            summary=summary,
            run_name=run_name,
        )

        linked_reports = rewrite_report_assets(
            run_dir=run_dir,
            report_assets=report_assets,
            source_candidates=source_candidates,
            dataset_tag=dataset_tag,
            run_timestamp=run_timestamp,
            summary=summary,
            run_name=run_name,
        )

        run_context.setdefault("report_assets", {})
        run_context["report_assets"]["pdf_files"] = linked_reports
        run_context.setdefault("available", {})
        run_context["available"]["report_pdf"] = bool(linked_reports)

        llm_evidence["report_assets"] = {"pdf_files": linked_reports}

        if not write_json(run_context_path, run_context, summary, run_name):
            summary.skipped.append(f"{run_name} (failed updating run_context.json)")
            continue
        if not write_json(llm_evidence_path, llm_evidence, summary, run_name):
            summary.skipped.append(f"{run_name} (failed updating llm_evidence.json)")
            continue

        if rebuild_bundle(run_dir, linked_reports, summary, run_name):
            summary.updated.append(run_name)
        else:
            summary.skipped.append(f"{run_name} (failed rebuilding llm_run_bundle)")

    return summary


def main() -> None:
    summary = normalize_runs()

    print("UPDATED_RUNS")
    for item in summary.updated:
        print(f"- {item}")

    print("SKIPPED_RUNS")
    for item in summary.skipped:
        print(f"- {item}")

    print("WARNINGS")
    for item in summary.warnings:
        print(f"- {item}")


if __name__ == "__main__":
    main()
