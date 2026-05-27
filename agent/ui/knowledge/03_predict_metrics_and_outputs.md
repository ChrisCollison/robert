# PREDICT metrics and outputs

## Purpose of this knowledge card
Use this document when a user asks about PREDICT, R2, RMSE, MAE, MCC, F1, accuracy, test-set predictions, external predictions, outliers, SHAP, PFI, or what the PREDICT folder contains.

## Common user questions this document should help answer
- What does PREDICT do?
- What do the PREDICT results mean?
- What is the difference between CV and test metrics?
- Why is my test RMSE worse than my CV RMSE?
- What does R2 mean here?
- What does scaled RMSE mean?
- Why are outliers reported?
- What is SHAP?
- What is PFI?
- What files should I inspect in the PREDICT folder?

## Plain-English summary
The PREDICT step takes the best models found by GENERATE and evaluates how well they predict. It reports model metrics, creates predictions, checks for outliers, and analyzes which descriptors appear important.

For a chemist, PREDICT is where the model becomes interpretable: it shows how well the model worked, which points were difficult, and which features may be driving the prediction.

## Official ROBERT behavior
PREDICT uses models obtained from the GENERATE module. For regression, it calculates R2, MAE, and RMSE. For classification, it calculates accuracy, F1 score, and MCC. It can predict the internal test set and, when supplied, an external test CSV.

PREDICT also performs:

- Outlier analysis.
- SHAP feature analysis.
- PFI feature analysis.
- Prediction CSV generation.
- Plots for No PFI and PFI models.

## Key regression metrics

### R2
R2 measures how well the predicted values follow the measured values. Higher is usually better. However, R2 alone can be misleading, especially for small datasets or narrow y-value ranges.

Plain-English explanation: R2 asks whether the model captures the trend.

Warning sign: A low R2 means the predicted values are not tracking the measured values well. A high R2 should still be checked against RMSE, VERIFY tests, and test-set performance.

### RMSE
RMSE is the root mean squared error. It measures prediction error in the units of the target value. Larger errors are penalized more strongly.

Plain-English explanation: RMSE asks how far off the predictions are, with extra penalty for large misses.

Warning sign: A high RMSE means the model's numerical predictions may not be useful, even if the trend looks acceptable.

### MAE
MAE is the mean absolute error. It measures average absolute prediction error in the units of the target value.

Plain-English explanation: MAE asks about the typical prediction miss.

Warning sign: MAE can be easier to interpret than RMSE, but it is less sensitive to large outliers.

### Scaled RMSE
Scaled RMSE expresses the RMSE relative to the range of target values. This helps compare errors across datasets with different y-value scales.

Plain-English explanation: scaled RMSE asks whether the error is small or large compared with the spread of the measured values.

## Key classification metrics

### Accuracy
Accuracy is the fraction of predictions that are correct. It is easy to understand but can be misleading for unbalanced classes.

### F1 score
F1 balances precision and recall. It is useful when one class is less common or when false positives and false negatives both matter.

### MCC
MCC is Matthew's correlation coefficient. It is often more informative than accuracy for unbalanced classification problems.

Plain-English explanation: MCC asks whether the classifier is doing better than a simple or biased guess, while accounting for all parts of the confusion matrix.

## CV predictions versus test predictions

### Cross-validation predictions
Cross-validation estimates how well the model performs across repeated splits of the training/validation data. It is useful for model selection and stability checks.

### Test-set predictions
The test set is held out from model optimization. It is a more direct check of how the model performs on data not used during tuning.

### Why the test set can be worse than CV
A worse test result can mean:

- The model is overfitted.
- The test set contains harder or more extreme points.
- The dataset is too small for a stable split.
- The y-value distribution is unbalanced.
- The descriptors do not generalize well.
- A few outliers dominate the test-set error.

A worse test result does not automatically mean the model is useless, but it lowers confidence.

## Outlier analysis
ROBERT identifies points with unusually high prediction errors relative to the training error distribution. The default threshold uses a t-value of 2, measured in standard-deviation units.

Plain-English explanation: outlier analysis asks which molecules, reactions, or entries the model missed badly compared with typical errors.

Outliers may indicate:

- Experimental measurement issues.
- Incorrect or inconsistent data entries.
- Compounds outside the chemical space of the training data.
- Missing descriptors for important chemistry.
- Mechanistically different cases.
- A model limitation rather than a data error.

The assistant should not automatically call an outlier a bad datapoint. It should say the point is worth inspecting.

## SHAP feature analysis
SHAP estimates how individual descriptors contribute to model predictions.

Plain-English explanation: SHAP asks which descriptors push predictions higher or lower for specific datapoints.

Use SHAP when the user asks:

- Why did the model predict this value?
- Which descriptors matter for this molecule or reaction?
- Is the model chemically interpretable?

## PFI feature analysis
PFI stands for permutation feature importance. ROBERT shuffles one descriptor at a time and checks how much worse the model gets.

Plain-English explanation: PFI asks which descriptors the model relies on most for overall prediction performance.

Use PFI when the user asks:

- Which descriptors are most important overall?
- Why did ROBERT keep or remove descriptors?
- What is the difference between No PFI and PFI models?

## No PFI versus PFI models
ROBERT can compare models using all selected descriptors with models using descriptors filtered by permutation feature importance.

- No PFI model: uses the descriptor set without PFI filtering.
- PFI model: uses a smaller descriptor set based on feature importance.

A PFI model may be more interpretable and may reduce overfitting, but it is not automatically better in every case.

## What the assistant should do with this information
When explaining PREDICT results:

1. Report the relevant metric values from the specific run.
2. Compare CV and test behavior.
3. Mention whether No PFI or PFI performed better.
4. Identify outliers if available.
5. Explain feature importance cautiously and chemically.
6. Avoid claiming causation from feature importance alone.

## Useful next actions for users
- Inspect any outliers by name.
- Compare No PFI and PFI models.
- Check whether top descriptors make chemical sense.
- Compare RMSE or MAE to the practical error tolerance of the chemistry problem.
- Inspect whether the test set covers the target range.
- Add datapoints similar to poorly predicted cases.

## Search keywords and aliases
PREDICT, prediction, predictions, R2, r squared, RMSE, root mean squared error, MAE, mean absolute error, scaled RMSE, MCC, F1, accuracy, CV, cross-validation, test set, external test set, outlier, outliers, t-value, standard deviation, SHAP, shap values, PFI, permutation feature importance, No PFI, PFI model, feature importance, descriptor importance, prediction error, test RMSE, CV RMSE.
