# CV, test gaps, uncertainty, and extrapolation

## Purpose of this knowledge card
Use this document when a user asks why cross-validation and test-set performance differ, why the test error is worse, why uncertainty is high, what sorted CV means, or whether the model can extrapolate.

## Common user questions this document should help answer
- Why is my test RMSE worse than CV?
- What does a CV/test gap mean?
- What does cross-validation tell me?
- What does the test set tell me?
- Why does ROBERT care about standard deviation?
- What does high uncertainty mean?
- What is sorted cross-validation?
- Is my model extrapolating?
- Why does ROBERT penalize extrapolation behavior?

## Plain-English summary
Cross-validation and test-set performance answer related but different questions.

Cross-validation asks: how stable is the model when trained and evaluated on different portions of the available modeling data?

The test set asks: how well does the selected model work on held-out points that were not used during model optimization?

If both look good, confidence increases. If cross-validation looks good but the test set looks poor, ROBERT treats that as a warning.

## Cross-validation in plain language
Cross-validation repeatedly divides the data into training and validation portions. The model is trained on one part and tested on another. This process is repeated so ROBERT can estimate how stable the model is.

Cross-validation is useful because a single split can be lucky or unlucky, especially with small chemistry datasets.

## Test set in plain language
The test set is held out before or during model selection and is not used to tune the model. It gives a more independent check of model performance.

A good test set should represent the chemical and target-value range the model is expected to predict.

## What a CV/test gap means
A CV/test gap happens when cross-validation performance and test-set performance differ substantially.

Possible causes include:

- Overfitting to the training/validation data.
- A test set that contains more difficult compounds or reactions.
- A test set that samples a sparse or extreme part of the y-value range.
- Too few datapoints for a stable split.
- Descriptor mismatch for the test-set compounds.
- Outliers in the test set.
- Chemical classes in the test set that are not well represented in training.

A CV/test gap is a warning, not a final diagnosis. The assistant should connect it to the actual data profile and ROBERT outputs.

## ROBERT score logic for CV/test agreement
For regression, ROBERT compares scaled RMSE from the test set against scaled RMSE from cross-validation. When test scaled RMSE is much larger than CV scaled RMSE, confidence decreases.

For classification, ROBERT compares MCC behavior between model and CV results. Larger differences imply higher uncertainty.

## Standard deviation and uncertainty
ROBERT estimates uncertainty using variability across repeated cross-validation predictions. If predictions vary a lot across repeated refits, the model is sensitive to which datapoints are included in training.

Plain-English explanation: if the model gives noticeably different answers depending on the training split, the prediction is less stable.

High uncertainty may indicate:

- Small dataset.
- Sparse chemical space.
- Noisy target values.
- Too many descriptors relative to datapoints.
- Weak descriptor-target relationship.
- Unstable model family for the dataset.

## 95% confidence interval approximation
ROBERT uses the average standard deviation from repeated cross-validation predictions and multiplies it by 4 to approximate a 95% confidence interval across the y range.

Plain-English explanation: ROBERT asks whether the model's uncertainty is small or large relative to the range of measured target values.

If the estimated interval spans a large fraction of the y range, then predictions may not be precise enough to guide decisions.

## Sorted cross-validation and extrapolation
Sorted cross-validation sorts the target values from low to high and evaluates performance across folds that represent different target-value regions.

Plain-English explanation: sorted CV asks whether the model works only in the middle of the data or whether it also behaves acceptably near low and high target values.

Poor sorted-CV behavior may suggest:

- Weak extrapolation ability.
- Sparse coverage at the extremes of y.
- Different mechanisms in low versus high regions.
- A need for more datapoints in underrepresented target-value ranges.

## How to explain this to a chemist
A model is more trustworthy when it behaves consistently across different checks. If CV is good but the test set is bad, the model may have learned a pattern that does not generalize to the held-out compounds. If uncertainty is high, predictions may change too much depending on the training split. If sorted CV is weak, the model may struggle outside well-sampled regions.

## What the assistant should do with this information
When explaining a specific run:

1. Compare CV and test metrics directly.
2. State whether the test result is similar, moderately worse, or much worse than CV.
3. Check whether outliers explain much of the gap.
4. Check whether the test set covers sparse or extreme y regions.
5. Mention uncertainty only when the ROBERT output provides it.
6. Avoid saying the model is overfit unless the evidence supports that conclusion.

## Useful next actions for users
- Inspect the y-value distribution.
- Identify whether the test-set points are chemically different from the training points.
- Review outliers and high-error points.
- Add data in sparse target-value regions.
- Consider whether the descriptor set captures the chemistry of low and high target values.
- Compare No PFI and PFI models.
- Treat external predictions cautiously if uncertainty is large.

## Search keywords and aliases
CV, cross-validation, cross validation, test set, test RMSE, CV RMSE, test error, CV error, CV/test gap, test versus CV, validation, held-out set, overfitting, generalization, uncertainty, standard deviation, prediction SD, 95 confidence interval, confidence interval, sorted CV, sorted cross-validation, extrapolation, interpolation, sparse y range, y distribution, unstable split, unstable model.
