# Classification Validation Report

Date: 2026-05-16
Run folder: `agent/run_archive/20260516_150946__TOF_class`
Dataset: `Databases/Clasification/AQME-ROBERT_interpret_TOF_clasif.csv`

## Objective

Validate wrapper -> extractor -> diagnosis for a real classification run and confirm classification-safe parsing behavior.

## Execution Summary

1. Ran ROBERT classification workflow:
   - `python -m robert --csv_name Databases/Clasification/AQME-ROBERT_interpret_TOF_clasif.csv --names code_name --y TOF_class --type clas --model [RF] --init_points 1 --n_iter 1`
2. Archived outputs into a new run folder with `CURATE`, `GENERATE`, `VERIFY`, `PREDICT`.
3. Ran `agent/extract_context.ipynb` on the new run.
4. Ran `agent/diagnose_score.ipynb` on the generated `run_context.json`.

## Findings

### Initial issue discovered
- `pred_type` was `None` and classification metrics were not parsed.
- Root cause: parser expected MCC-first format, but ROBERT output used:
  - `Accur. = ..., F1 score = ..., MCC = ...`

### Fix implemented
- Updated classification regex logic in `agent/extract_context.ipynb` to support:
  - `Accur. / F1 score / MCC` ordering
  - legacy MCC-first fallback
- Updated pred_type detection to classify both MCC-first and Accur-first CV lines as `clas`.
- Updated feature-importance header handling to include `Influence on MCC`.

### Post-fix validation results
- `pred_type`: `clas`
- No PFI metrics parsed:
  - `mcc_cv=0.19`, `mcc_test=0.33`
  - `f1_cv=0.59`, `f1_test=0.5`
  - `accuracy_cv=0.59`, `accuracy_test=0.5`
- PFI metrics parsed:
  - `mcc_cv=0.61`, `mcc_test=0.33`
  - `f1_cv=0.81`, `f1_test=0.5`
  - `accuracy_cv=0.81`, `accuracy_test=0.5`
- VERIFY parse for classification:
  - no_pfi `passed=3`, `failed=0`, `unclear=0`
  - pfi `passed=3`, `failed=0`, `unclear=0`
- Diagnosis notebook completed successfully and produced:
  - `diagnosis.json`
  - `diagnosis_summary.md`

## Status

Classification path validation: PASS after parser fix.

## Residual Notes

- `score.no_pfi` and `score.pfi` remain null in this workflow (known/report-driven behavior).
- Reported artifact naming for the two graph paths still follows existing parser assumptions and should be reviewed separately if strict semantic labeling is required.
