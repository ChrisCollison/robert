# ROBERT Diagnosis Summary

- Diagnosed at: 2026-05-16T19:11:15Z
- Prediction type: clas
- Model: RF
- Dataset: /Users/cjcscha/ROBERT/helper_rob/robert/Databases/Clasification/AQME-ROBERT_interpret_TOF_clasif.csv

## Operating Mode
- ROBERT is authoritative for model scores and metrics.
- This artifact is extracted context for LLM explanation, not a competing score.
- PDF is for user display; LLM should use extracted raw text context and image references.

## ROBERT Score (As Extracted)
- Not available in this run_context.json (null placeholders).

## NO_PFI (ROBERT-Reported Evidence)
- MCC CV/Test: 0.19 / 0.33
- Train/Test points: 14 / 4
- Descriptors: 6 (['LUMO', 'Pt_Dipole moment', 'Pt_Fukui dual', 'Pt_Normaliz. electrophil.', 'Pt_Pyramidalization', 'SASA'])
- Train:descriptor string: 14:6

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
- [info] predict_n_train: ROBERT reported n_train = 14.
- [info] predict_n_test: ROBERT reported n_test = 4.
- [info] predict_n_descriptors: ROBERT reported n_descriptors = 6.
- [info] predict_points_descp_ratio: ROBERT reported points_descp_ratio = 14:6.

## PFI (ROBERT-Reported Evidence)
- MCC CV/Test: 0.61 / 0.33
- Train/Test points: 14 / 4
- Descriptors: 1 (['Pt_Pyramidalization'])
- Train:descriptor string: 14:1

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
- [info] predict_n_train: ROBERT reported n_train = 14.
- [info] predict_n_test: ROBERT reported n_test = 4.
- [info] predict_n_descriptors: ROBERT reported n_descriptors = 1.
- [info] predict_points_descp_ratio: ROBERT reported points_descp_ratio = 14:1.

## Derived Convenience Values
- These are convenience transforms from ROBERT-reported fields and are not ROBERT score components.
- no_pfi: {'train_to_descriptor_ratio': {'value': 2.333, 'from': 'predict.no_pfi.points_descp_ratio', 'label': 'derived convenience value'}}
- pfi: {'train_to_descriptor_ratio': {'value': 14.0, 'from': 'predict.pfi.points_descp_ratio', 'label': 'derived convenience value'}}

## Notes
- ROBERT score not yet populated in run_context.json for this run. Use ROBERT report outputs as authoritative source when available.