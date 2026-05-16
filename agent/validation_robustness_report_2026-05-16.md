# Missing-File Robustness Validation Report

Date: 2026-05-16
Run folder: `agent/run_archive/20260516_151123__TOF_class_incomplete`
Scenario: intentionally incomplete archive containing only `outputs/PREDICT` plus `run_manifest.json`.

## Objective

Confirm extractor and diagnosis remain null-safe when `VERIFY`, `CURATE`, and `GENERATE` outputs are missing.

## Test Setup

1. Created synthetic incomplete run by copying only `PREDICT` from a valid classification run.
2. Left `VERIFY_data.dat`, `CURATE_data.dat`, and `GENERATE_data.dat` absent.
3. Ran `agent/extract_context.ipynb` on this run.
4. Ran `agent/diagnose_score.ipynb` on resulting `run_context.json`.

## Results

### Extractor behavior
- Notebook execution: PASS (no crash).
- Availability flags in `run_context.json`:
  - `predict: true`
  - `verify: false`
  - `curate: false`
  - `generate: false`
- Classification metrics still parsed from PREDICT:
  - no_pfi `mcc_cv=0.19`, `mcc_test=0.33`
  - pfi `mcc_cv=0.61`, `mcc_test=0.33`
- Missing sections were represented as null/empty values (no fabricated values):
  - `verify.*` counts and test results set to null/empty
  - `curate.*` numeric summaries set to null
  - `generate.model_screening_summary` empty
- Parser warning retained and explicit:
  - ROBERT score not found in available `.dat` files.

### Diagnosis behavior
- Notebook execution: PASS (no crash).
- `diagnosis.json` and `diagnosis_summary.md` were generated.
- Missing VERIFY evidence was surfaced as explicit missing-evidence observations rather than causing exceptions.

## Key Note on Notebook State

During validation, full null-safe representation required executing all relevant extractor cells (`PREDICT`, `VERIFY`, `CURATE/GENERATE`) before final write. This confirms robustness in output schema, but also highlights that partial cell execution can retain stale in-memory values in an interactive notebook session.

## Status

Missing-file robustness validation: PASS.
