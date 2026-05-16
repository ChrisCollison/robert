# ROBERT Diagnosis Summary

- Diagnosed at: 2026-05-15T20:57:15Z
- Prediction type: reg
- Model: MVL
- Dataset: /Users/cjcscha/ROBERT/helper_rob/robert/Databases/Regression/Hvapor.csv

## Operating Mode
- ROBERT is authoritative for model scores and metrics.
- This artifact is extracted context for LLM explanation, not a competing score.
- PDF is for user display; LLM should use extracted raw text context and image references.

## ROBERT Score (As Extracted)
- Not available in this run_context.json (null placeholders).

## NO_PFI (ROBERT-Reported Evidence)
- R2 CV/Test: 0.77 / 0.78
- RMSE CV/Test: 5.7 / 5.5
- MAE CV/Test: 4.7 / 4.7
- Train/Test points: 106 / 27
- Descriptors: 3 (['Hardness', 'SGBP', 'g3'])
- Train:descriptor string: 106:3

### VERIFY
- failed/unclear/passed: 0 / 0 / 3
- flawed_mod_score (ROBERT): 0
- test_results: ['y_mean: PASSED', 'y_shuffle: PASSED', 'onehot: PASSED']

### Observations
- [PASSED] verify_y_mean: ROBERT VERIFY: y_mean -> PASSED
- [PASSED] verify_y_shuffle: ROBERT VERIFY: y_shuffle -> PASSED
- [PASSED] verify_onehot: ROBERT VERIFY: onehot -> PASSED
- [info] verify_failed_tests: ROBERT reported failed_tests = 0.
- [info] verify_unclear_tests: ROBERT reported unclear_tests = 0.
- [info] verify_passed_tests: ROBERT reported passed_tests = 3.
- [info] verify_flawed_mod_score: ROBERT reported flawed_mod_score = 0.
- [info] predict_n_train: ROBERT reported n_train = 106.
- [info] predict_n_test: ROBERT reported n_test = 27.
- [info] predict_n_descriptors: ROBERT reported n_descriptors = 3.
- [info] predict_points_descp_ratio: ROBERT reported points_descp_ratio = 106:3.
- [info] predict_train_outlier_pct: ROBERT reported train_outlier_pct = 3.8.
- [info] predict_test_outlier_pct: ROBERT reported test_outlier_pct = 0.0.

## PFI (ROBERT-Reported Evidence)
- R2 CV/Test: 0.77 / 0.79
- RMSE CV/Test: 5.7 / 5.2
- MAE CV/Test: 4.7 / 4.5
- Train/Test points: 106 / 27
- Descriptors: 2 (['SGBP', 'Hardness'])
- Train:descriptor string: 106:2

### VERIFY
- failed/unclear/passed: 0 / 0 / 3
- flawed_mod_score (ROBERT): 0
- test_results: ['y_mean: PASSED', 'y_shuffle: PASSED', 'onehot: PASSED']

### Observations
- [PASSED] verify_y_mean: ROBERT VERIFY: y_mean -> PASSED
- [PASSED] verify_y_shuffle: ROBERT VERIFY: y_shuffle -> PASSED
- [PASSED] verify_onehot: ROBERT VERIFY: onehot -> PASSED
- [info] verify_failed_tests: ROBERT reported failed_tests = 0.
- [info] verify_unclear_tests: ROBERT reported unclear_tests = 0.
- [info] verify_passed_tests: ROBERT reported passed_tests = 3.
- [info] verify_flawed_mod_score: ROBERT reported flawed_mod_score = 0.
- [info] predict_n_train: ROBERT reported n_train = 106.
- [info] predict_n_test: ROBERT reported n_test = 27.
- [info] predict_n_descriptors: ROBERT reported n_descriptors = 2.
- [info] predict_points_descp_ratio: ROBERT reported points_descp_ratio = 106:2.
- [info] predict_train_outlier_pct: ROBERT reported train_outlier_pct = 4.7.
- [info] predict_test_outlier_pct: ROBERT reported test_outlier_pct = 0.0.

## Derived Convenience Values
- These are convenience transforms from ROBERT-reported fields and are not ROBERT score components.
- no_pfi: {'train_to_descriptor_ratio': {'value': 35.333, 'from': 'predict.no_pfi.points_descp_ratio', 'label': 'derived convenience value'}}
- pfi: {'train_to_descriptor_ratio': {'value': 53.0, 'from': 'predict.pfi.points_descp_ratio', 'label': 'derived convenience value'}}

## Notes
- ROBERT score not yet populated in run_context.json for this run. Use ROBERT report outputs as authoritative source when available.