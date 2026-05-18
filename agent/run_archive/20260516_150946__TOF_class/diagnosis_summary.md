# ROBERT Diagnosis Summary

- Diagnosed at: 2026-05-17T01:08:37Z
- Prediction type: clas
- Model: RF
- Dataset: /Users/cjcscha/ROBERT/helper_rob/robert/Databases/Clasification/AQME-ROBERT_interpret_TOF_clasif.csv

## Operating Mode
- ROBERT is authoritative for model scores and metrics.
- This artifact is extracted context for explanation, not a competing score.
- PDF is for user display; this extracted context is the ground truth for the UI.

## ROBERT Score (As Extracted)
- Not available in this run_context.json (null placeholders).

## Interpretation (What This Means)
Only 14.0 training molecules for 6.0 descriptors (ratio 2.3:1). Cross-validation estimates have high variance at this ratio. Model performance may look better or worse than it truly is, and generalisation to new chemical space is uncertain. All VERIFY tests PASSED, but MCC CV = 0.19 is below 0.5. This usually means the model is internally consistent (not fitting noise), but the chosen descriptors do not capture the chemistry that drives the target property. Consider whether the descriptors relate to the physical mechanism of your reaction or property. ROBERT warned: x  WARNING! Noticeable correlations observed (up to r = 0.82 or R2 = 0.67, for Pt_Fukui dual and Pt_Normaliz. electrophil.) Correlated descriptors can inflate apparent model performance in cross-validation, because the model can reconstruct a removed descriptor from correlated ones. The PFI variant (if available) uses only the most important descriptor, which avoids this issue.

## NO_PFI (ROBERT-Reported Evidence)
- MCC CV/Test: 0.19 / 0.33
- Train/Test points: 14 / 4
- Descriptors: 6 (['LUMO', 'Pt_Dipole moment', 'Pt_Fukui dual', 'Pt_Normaliz. electrophil.', 'Pt_Pyramidalization', 'SASA'])
- Train:descriptor string: 14:6

### VERIFY
- failed/unclear/passed: 0 / 0 / 3
- flawed_mod_score (ROBERT): 0
- test_results: ['y_mean: PASSED', 'y_shuffle: PASSED', 'onehot: PASSED']

### What This Means
- [WARNING] Only 14.0 training molecules for 6.0 descriptors (ratio 2.3:1). Cross-validation estimates have high variance at this ratio. Model performance may look better or worse than it truly is, and generalisation to new chemical space is uncertain.
- [WARNING] All VERIFY tests PASSED, but MCC CV = 0.19 is below 0.5. This usually means the model is internally consistent (not fitting noise), but the chosen descriptors do not capture the chemistry that drives the target property. Consider whether the descriptors relate to the physical mechanism of your reaction or property.
- [INFO] Descriptor "Pt_Pyramidalization" accounts for 100% of feature importance. This may mean the other descriptors are redundant, or that the model relies heavily on a single chemical property. Consider whether this descriptor captures the core mechanism of your reaction or property.
- [WARNING] ROBERT warned: x  WARNING! Noticeable correlations observed (up to r = 0.82 or R2 = 0.67, for Pt_Fukui dual and Pt_Normaliz. electrophil.) Correlated descriptors can inflate apparent model performance in cross-validation, because the model can reconstruct a removed descriptor from correlated ones. The PFI variant (if available) uses only the most important descriptor, which avoids this issue.

### All Observations
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
- [warning] interp_low_n_per_descriptor: Only 14.0 training molecules for 6.0 descriptors (ratio 2.3:1). Cross-validation estimates have high variance at this ratio. Model performance may look better or worse than it truly is, and generalisation to new chemical space is uncertain.
- [warning] interp_consistent_but_weak: All VERIFY tests PASSED, but MCC CV = 0.19 is below 0.5. This usually means the model is internally consistent (not fitting noise), but the chosen descriptors do not capture the chemistry that drives the target property. Consider whether the descriptors relate to the physical mechanism of your reaction or property.
- [info] interp_dominant_feature: Descriptor "Pt_Pyramidalization" accounts for 100% of feature importance. This may mean the other descriptors are redundant, or that the model relies heavily on a single chemical property. Consider whether this descriptor captures the core mechanism of your reaction or property.
- [warning] interp_descriptor_correlation: ROBERT warned: x  WARNING! Noticeable correlations observed (up to r = 0.82 or R2 = 0.67, for Pt_Fukui dual and Pt_Normaliz. electrophil.) Correlated descriptors can inflate apparent model performance in cross-validation, because the model can reconstruct a removed descriptor from correlated ones. The PFI variant (if available) uses only the most important descriptor, which avoids this issue.

## PFI (ROBERT-Reported Evidence)
- MCC CV/Test: 0.61 / 0.33
- Train/Test points: 14 / 4
- Descriptors: 1 (['Pt_Pyramidalization'])
- Train:descriptor string: 14:1

### VERIFY
- failed/unclear/passed: 0 / 0 / 3
- flawed_mod_score (ROBERT): 0
- test_results: ['y_mean: PASSED', 'y_shuffle: PASSED', 'onehot: PASSED']

### What This Means
- [WARNING] MCC CV = 0.61, Test = 0.33 (gap = 0.28). CV performance was more optimistic than the held-out test. This can happen when training and test molecules come from different chemical regions, or when the dataset is too small for stable splits.
- [INFO] Descriptor "Pt_Pyramidalization" accounts for 100% of feature importance. This may mean the other descriptors are redundant, or that the model relies heavily on a single chemical property. Consider whether this descriptor captures the core mechanism of your reaction or property.

### All Observations
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
- [warning] interp_cv_optimistic: MCC CV = 0.61, Test = 0.33 (gap = 0.28). CV performance was more optimistic than the held-out test. This can happen when training and test molecules come from different chemical regions, or when the dataset is too small for stable splits.
- [info] interp_dominant_feature: Descriptor "Pt_Pyramidalization" accounts for 100% of feature importance. This may mean the other descriptors are redundant, or that the model relies heavily on a single chemical property. Consider whether this descriptor captures the core mechanism of your reaction or property.

## Derived Convenience Values
- These are convenience transforms from ROBERT-reported fields and are not ROBERT score components.
- no_pfi: {'train_to_descriptor_ratio': {'value': 2.333, 'from': 'predict.no_pfi.points_descp_ratio', 'label': 'derived convenience value'}}
- pfi: {'train_to_descriptor_ratio': {'value': 14.0, 'from': 'predict.pfi.points_descp_ratio', 'label': 'derived convenience value'}}

## Notes
- ROBERT score not yet populated in run_context.json for this run. Use ROBERT report outputs as authoritative source when available.