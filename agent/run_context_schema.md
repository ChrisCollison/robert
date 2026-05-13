# run_context.json Schema

This document defines all fields that `extract_context.py` will attempt to populate.
Every field is `null` if the source data is missing or unparseable — parsers must never raise on missing data.

The schema is grouped by source module.

---

## Extractor V1 Must-Have Subset

This is the implementation target for the first thin slice.
Only these fields are required for V1. Other schema fields remain planned for later expansion.

### V1 scope

- Primary files: `PREDICT/PREDICT_data.dat` and `VERIFY/VERIFY_data.dat`
- Optional provenance files (if easy): `CURATE/CURATE_data.dat`, `GENERATE/GENERATE_data.dat`
- No diagnosis rules in extractor V1
- No LLM output in extractor V1

### V1 required keys

| Field | Type | Required in V1 | Notes |
|---|---|---|---|
| `schema_version` | str | Yes | Set to `"1.0"` for first extractor drop |
| `extracted_at` | str | Yes | ISO 8601 UTC timestamp |
| `results_dir` | str | Yes | Absolute path provided by CLI |
| `pred_type` | str or null | Yes | Parse from PREDICT if present |
| `ml_model` | str or null | Yes | Parse from PREDICT if present |
| `available.predict` | bool | Yes | True only if `PREDICT_data.dat` found and readable |
| `available.verify` | bool | Yes | True only if `VERIFY_data.dat` found and readable |
| `available.curate` | bool | Yes | False if CURATE not parsed in this run |
| `available.generate` | bool | Yes | False if GENERATE not parsed in this run |
| `available.test_set` | bool | Yes | True if test-set metrics detected in PREDICT |
| `available.pfi` | bool | Yes | True if PFI block detected |
| `predict.no_pfi.cv_type` | str or null | Yes | |
| `predict.no_pfi.points_descp_ratio` | str or null | Yes | Keep raw string in V1 |
| `predict.no_pfi.r2_cv` | float or null | Yes | For clas, this is MCC_cv |
| `predict.no_pfi.r2_test` | float or null | Yes | For clas, this is MCC_test |
| `predict.no_pfi.rmse_cv` | float or null | Yes | null for classification |
| `predict.no_pfi.rmse_test` | float or null | Yes | null for classification |
| `predict.pfi.cv_type` | str or null | Yes | Must exist as key even if PFI absent |
| `predict.pfi.r2_cv` | float or null | Yes | Must exist as key even if PFI absent |
| `predict.pfi.r2_test` | float or null | Yes | Must exist as key even if PFI absent |
| `predict.pfi.rmse_cv` | float or null | Yes | Must exist as key even if PFI absent |
| `predict.pfi.rmse_test` | float or null | Yes | Must exist as key even if PFI absent |
| `verify.no_pfi.failed_tests` | int or null | Yes | |
| `verify.no_pfi.test_results` | list[str] or null | Yes | PASS/UNCLEAR/FAILED raw lines |
| `verify.no_pfi.flawed_mod_score` | int or null | Yes | |
| `verify.pfi.failed_tests` | int or null | Yes | Must exist as key even if PFI absent |
| `verify.pfi.test_results` | list[str] or null | Yes | Must exist as key even if PFI absent |
| `verify.pfi.flawed_mod_score` | int or null | Yes | Must exist as key even if PFI absent |
| `score.no_pfi` | int or null | Yes | Null in V1 if final score not reconstructed yet |
| `score.pfi` | int or null | Yes | Null in V1 if final score not reconstructed yet |

### V1 parser behavior contract

1. Missing file: do not raise, set matching `available.*` to `false`, and keep related fields as `null`.
2. Missing section inside existing file: do not raise, keep section fields as `null`.
3. Type coercion failures: keep field as `null` and append a warning string.
4. Unknown text lines: ignore by default; optionally collect under `parser_warnings`.
5. Output shape must be stable: all V1 required keys must always be present.

### V1 acceptance criteria

1. One complete regression run produces a valid `run_context.json` with all V1 keys populated or null.
2. One complete classification run produces a valid `run_context.json` with RMSE fields null where not applicable.
3. One intentionally incomplete run does not crash and sets `available.*` correctly.
4. Re-running extraction on the same folder changes only timestamp fields unless source outputs changed.

---

## Top-level metadata

| Field | Type | Source | Notes |
|---|---|---|---|
| `schema_version` | str | hardcoded | `"1.0"` — bump when schema changes |
| `extracted_at` | str | runtime | ISO 8601 UTC timestamp |
| `results_dir` | str | CLI arg | Absolute path to the ROBERT run folder |
| `pred_type` | str or null | PREDICT_data.dat | `"reg"` or `"clas"` |
| `ml_model` | str or null | PREDICT_data.dat | e.g. `"RF"`, `"GBM"`, `"NN"` |

---

## CURATE section

Source: `CURATE/CURATE_data.dat`

| Field | Type | Notes |
|---|---|---|
| `curate.n_initial` | int or null | Number of datapoints before curation |
| `curate.n_final` | int or null | Number of datapoints after curation |
| `curate.n_dropped` | int or null | Derived: `n_initial - n_final` |
| `curate.n_features_initial` | int or null | Descriptors/columns before curation |
| `curate.n_features_final` | int or null | Descriptors after curation |
| `curate.warnings` | list[str] | Any curation warning lines detected |

---

## GENERATE section

Source: `GENERATE/GENERATE_data.dat`, `GENERATE/Best_model/No_PFI/*.csv`, `GENERATE/Best_model/PFI/*.csv`

| Field | Type | Notes |
|---|---|---|
| `generate.best_model_no_pfi` | str or null | Model type selected for No PFI run |
| `generate.best_model_pfi` | str or null | Model type selected for PFI run |
| `generate.split_type` | str or null | e.g. `"KN"`, `"RND"`, `"STRAT"` |
| `generate.train_size` | int or null | Number of training points |
| `generate.test_size` | int or null | Number of test points |

---

## PREDICT section (per-model suffix: `No_PFI` and `PFI`)

Source: `PREDICT/PREDICT_data.dat`  
Fields are replicated for each suffix (`no_pfi` and `pfi`).

| Field | Type | Notes |
|---|---|---|
| `predict.{suffix}.cv_type` | str or null | e.g. `"10x 5-fold CV"` |
| `predict.{suffix}.points_descp_ratio` | str or null | Raw ratio string from dat file |
| `predict.{suffix}.r2_cv` | float or null | R² (reg) or MCC (clas) from CV |
| `predict.{suffix}.rmse_cv` | float or null | RMSE from CV (reg only, else null) |
| `predict.{suffix}.scaled_rmse_cv_pct` | float or null | RMSE as % of y-range (reg only) |
| `predict.{suffix}.r2_test` | float or null | R² (reg) or MCC (clas) from test set |
| `predict.{suffix}.rmse_test` | float or null | RMSE from test set (reg only) |
| `predict.{suffix}.scaled_rmse_test_pct` | float or null | RMSE as % of y-range (reg only) |
| `predict.{suffix}.y_range` | float or null | y-range of dataset (reg only) |
| `predict.{suffix}.cv_sd` | float or null | Average SD in test set |
| `predict.{suffix}.cv_4sd` | float or null | 4× SD |
| `predict.{suffix}.cv_range_cov` | float or null | Fraction of y-range covered by 4×SD |
| `predict.{suffix}.factor_scaled_rmse` | float or null | Ratio of test RMSE to CV RMSE |

### Derived score sub-components (reg)

| Field | Type | Notes |
|---|---|---|
| `predict.{suffix}.scores.cv_score_rmse` | int or null | 0–2 from scaled RMSE thresholds |
| `predict.{suffix}.scores.cv_penalty_r2` | int or null | 0 to -2 from R² thresholds |
| `predict.{suffix}.scores.cv_score_combined` | int or null | Sum of above, floored at 0 |
| `predict.{suffix}.scores.test_score_rmse` | int or null | 0–2 |
| `predict.{suffix}.scores.test_penalty_r2` | int or null | 0 to -2 |
| `predict.{suffix}.scores.test_score_combined` | int or null | Floored at 0 |
| `predict.{suffix}.scores.cv_sd_score` | int or null | 0–2 from SD coverage |
| `predict.{suffix}.scores.diff_scaled_rmse_score` | int or null | 0–2 from CV/test RMSE ratio |

### Derived score sub-components (clas)

| Field | Type | Notes |
|---|---|---|
| `predict.{suffix}.scores.cv_score_combined` | int or null | From MCC thresholds |
| `predict.{suffix}.scores.test_score_combined` | int or null | From MCC thresholds |
| `predict.{suffix}.scores.diff_mcc_score` | int or null | 0–2 from |MCC_test - MCC_cv| |
| `predict.{suffix}.scores.descp_score` | int or null | Descriptor ratio contribution |

---

## VERIFY section (per-model suffix)

Source: `VERIFY/VERIFY_data.dat`

| Field | Type | Notes |
|---|---|---|
| `verify.{suffix}.flawed_mod_score` | int or null | 0 to -2 per failed test, capped |
| `verify.{suffix}.failed_tests` | int or null | Count of FAILED tests |
| `verify.{suffix}.test_results` | list[str] or null | Raw result lines: PASS/UNCLEAR/FAILED |
| `verify.{suffix}.sorted_cv_score` | int or null | 0–N from sorted CV consistency |
| `verify.{suffix}.sorted_rmse_mcc_values` | list[float] or null | Raw sorted CV metric values |
| `verify.{suffix}.sorted_results` | list[str] or null | pass/fail/min/max labels per fold |

---

## Final score

| Field | Type | Notes |
|---|---|---|
| `score.no_pfi` | int or null | Final ROBERT score for No PFI model |
| `score.pfi` | int or null | Final ROBERT score for PFI model |
| `score.no_pfi_components` | dict or null | All sub-scores for No PFI |
| `score.pfi_components` | dict or null | All sub-scores for PFI |

---

## Presence flags

These are set by the extractor to tell the diagnosis layer what data was available.

| Field | Type | Notes |
|---|---|---|
| `available.curate` | bool | CURATE_data.dat found and readable |
| `available.generate` | bool | GENERATE_data.dat found and readable |
| `available.predict` | bool | PREDICT_data.dat found and readable |
| `available.verify` | bool | VERIFY_data.dat found and readable |
| `available.test_set` | bool | Test set results present in PREDICT |
| `available.pfi` | bool | PFI model results present |

---

## Design rules for parsers

1. Return `None` for any field that cannot be found — never raise on missing data.
2. Never hardcode absolute paths — accept `results_dir` as a parameter.
3. All numeric values should be stored as Python native types (`float`, `int`), not strings.
4. `available.*` flags must be set even when all sub-fields are null.
5. The schema version must be bumped (in code) any time a field is added, removed, or renamed.
