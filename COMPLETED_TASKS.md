# Completed Tasks

Purpose
- Append-only audit log of completed work.
- This is the source-of-truth for what has been done.

## 2026-04-24

### Branch and repository inspection
- Created and switched to branch: agent-score-explainer.
- Confirmed active branch via git branch.
- Located ROBERT score computation path in report_utils.calc_score.
- Located PDF generation path in report/report_utils.
- Mapped report dependencies on CURATE, GENERATE, VERIFY, and PREDICT outputs.
- Assessed safest initial files to parse for run_context.json.
- Reviewed AGENTS.md and README_AGENT.md for objective alignment.

### Documentation setup
- Added agent/REFERENCE_NOTES.md for persistent key findings.
- Added TODO.md with a proposed-plan section and stepwise task list.
- Added COMPLETED_TASKS.md for auditable progress tracking.

## 2026-05-13

### Run archiving workflow bootstrap
- Added `agent/robert_run_wrapper.ipynb` to run ROBERT optionally and archive module outputs per run.
- Implemented timestamp + dataset-name run folder naming under `agent/run_archive/`.
- Added output binning for `CURATE/`, `GENERATE/`, `VERIFY/`, and `PREDICT/` to avoid overwrite of generic output folders.
- Added per-run `run_manifest.json` capture with dataset path, command used, return code, and archived directories.
- Verified CLI option pattern uses `--csv_name` in ROBERT help text in `robert/utils.py`.

### Wrapper notebook command automation
- Updated `agent/robert_run_wrapper.ipynb` so `ROBERT_COMMAND` is auto-generated from `DATASET_CSV` plus a single `ROBERT_OPTIONS` dictionary.
- Added helper conversion of notebook options to CLI flags (`--key value` and bool-flag support).
- Added command preview print in execution cell to confirm the exact command before run.

### Diagnosis notebook implementation start
- Added `agent/diagnose_score.ipynb` as the rule-based diagnosis layer consuming `run_context.json`.
- Implemented deterministic score-component decomposition aligned to `robert/report_utils.py` thresholds for regression and classification branches.
- Implemented evidence-linked diagnostic flags for CV/test quality, VERIFY failures, outlier burden, quartile imbalance, and evidence gaps.
- Added artifact writing for per-run outputs: `diagnosis.json` and `diagnosis_summary.md`.
