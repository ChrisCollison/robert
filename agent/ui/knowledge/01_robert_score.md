# ROBERT score

## Purpose of this knowledge card
Use this document when a user asks about the ROBERT score, model reliability, whether a model can be trusted, why a score is low, why a score is moderate, or why good-looking metrics may still be misleading.

## Common user questions this document should help answer
- Why did I get this ROBERT score?
- What does my ROBERT score mean?
- Can I trust a model with this score?
- Why is my score low even though my RMSE or R2 looks good?
- Why does ROBERT care about y-shuffle or y-mean tests?
- What does a moderate ROBERT score mean?
- What makes a ROBERT model strong or weak?
- Why did ROBERT penalize my model?

## Plain-English summary
The ROBERT score is a reliability score for a machine-learning model. It is not just a measure of whether the model fits the data. It asks a more cautious question: does the model appear to make useful predictions for valid reasons?

A model can have a good R2, RMSE, MAE, accuracy, or MCC and still be unreliable. For example, a model may look good because the split was lucky, because the dataset is too small, because the descriptors are not meaningful, because the model is overfitted, or because a flawed baseline model performs almost as well.

The score is intended to help chemists interpret model quality without needing to be machine-learning experts.

## Official ROBERT behavior
ROBERT gives a score out of 10. The score combines several checks, including:

1. Performance against flawed or baseline models, especially VERIFY tests.
2. Cross-validation performance.
3. Test-set performance.
4. Agreement between cross-validation and test-set behavior.
5. Estimated uncertainty from repeated cross-validation.
6. Extrapolation behavior from sorted cross-validation.
7. Penalties when R2 or related metrics are poor.

The score is designed around modern best practices in chemical machine learning and around benchmarking by the ROBERT developers.

## Score interpretation
The official score ranges are grouped qualitatively:

- Very weak: very unreliable model.
- Weak: unreliable model.
- Moderate: somewhat reliable model.
- Strong: reliable model.

A moderate score does not always mean the model is useless. It often means the model may contain useful signal, but some evidence limits confidence. A weak or very weak score means the result should be interpreted cautiously and should not be treated as a robust predictor without further work.

## What usually lowers the score
Common reasons include:

- Too few datapoints.
- Unbalanced target values, such as many points in one region and few in another.
- Too few useful descriptors.
- Too many descriptors relative to datapoints.
- Strong disagreement between cross-validation and test-set performance.
- Poor R2, high scaled RMSE, or low MCC.
- Failed or unclear VERIFY tests.
- High uncertainty across repeated cross-validation predictions.
- Poor extrapolation behavior in sorted cross-validation.
- Outliers or unusual points that dominate the error.

## Key ROBERT score components in plain language

### Model vs flawed models
ROBERT checks whether the model is clearly better than deliberately flawed alternatives. If a flawed model performs similarly to the real model, the result may not be learning meaningful chemical signal.

Important flawed-model checks include:

- y-mean test: compares the model against predicting the mean or most common class.
- y-shuffle test: checks whether performance remains good after target values are shuffled.
- one-hot test: checks whether the model depends mostly on whether descriptor values are present rather than on their actual values.

### Cross-validation predictions
Cross-validation estimates how well the model behaves when it is repeatedly trained and tested on different portions of the dataset. ROBERT uses this to estimate whether the model is stable.

For regression, ROBERT considers scaled RMSE and R2. For classification, ROBERT uses MCC-related criteria.

### Test-set predictions
The test set is held out from model optimization. Strong test performance is important because it asks whether the model works on points it did not use during tuning.

### Test versus CV agreement
If the test error is much worse than the cross-validation error, the model may be overfit, the test set may be difficult, or the dataset split may expose limited generalization.

### Average standard deviation
ROBERT estimates prediction variability across repeated cross-validation predictions. High variability means the model's predictions are sensitive to which datapoints are used for training.

### Sorted cross-validation
Sorted cross-validation tests whether the model performs consistently across different regions of the target-value range. Poor behavior here can suggest problems with extrapolation or uneven coverage of the y range.

## How to explain this to a chemist
The score is like a confidence rating for the model. A high score means the model's predictions look good across several stress tests. A low score means ROBERT found reasons to doubt the model, even if one metric looks acceptable.

The score should be interpreted together with the dataset size, target-value coverage, descriptor quality, feature importance, outliers, and VERIFY tests.

## What the assistant should do with this information
When answering a user about a specific ROBERT score:

1. Start with the actual score and score category if available.
2. Identify which components contributed most to the score.
3. Separate specific evidence from general explanation.
4. Avoid saying the model is good or bad based on the score alone.
5. Suggest a few practical next steps grounded in the actual ROBERT output.

## Useful next actions for users
Depending on the evidence, suggest actions such as:

- Inspect failed or unclear VERIFY tests.
- Compare CV and test metrics.
- Check the y-value distribution and whether the test set covers the range.
- Inspect outliers and decide whether they are chemically meaningful or data errors.
- Review top descriptors from SHAP and PFI for chemical plausibility.
- Add datapoints in sparse regions of the target range.
- Improve descriptor quality or include descriptors better matched to the chemistry.
- Rerun ROBERT with a different split strategy only when there is a clear reason.

## Search keywords and aliases
ROBERT score, model score, why score, model reliability, trust model, weak model, moderate model, strong model, very weak model, poor score, low score, high score, score penalty, score components, score explanation, flawed models, y-mean, y-shuffle, one-hot, cross-validation, CV, test set, scaled RMSE, R2, MCC, overfitting, underfitting, uncertainty, sorted CV, extrapolation.
