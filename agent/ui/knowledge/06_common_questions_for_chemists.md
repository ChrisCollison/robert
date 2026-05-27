# Common ROBERT questions for chemists

## Purpose of this knowledge card
Use this document as a broad FAQ layer for natural-language user questions. It is intentionally written around how chemists may ask questions, not around software-documentation headings.

## Important response policy for the assistant
When answering a specific user's ROBERT run, use the actual ROBERT run values first. Use this FAQ only as explanatory background. Do not invent values, files, metrics, descriptors, or failed tests that are not present in the run context.

## Question: Why did I get this ROBERT score?
The ROBERT score reflects several kinds of evidence, not just one metric. A low or moderate score can result from weak CV or test performance, failed VERIFY tests, a large CV/test gap, high uncertainty, poor extrapolation behavior, outliers, too few datapoints, too many or too few useful descriptors, or poor chemical coverage.

For a specific run, inspect the score components, PREDICT metrics, VERIFY results, outliers, descriptor counts, and feature importance.

## Question: Can I trust this model?
Trust depends on the pattern of evidence. A model is more trustworthy when CV and test performance are both good, VERIFY tests pass, uncertainty is low, outliers are limited, and important descriptors make chemical sense.

A model is less trustworthy when it performs well only under one metric, fails sanity checks, has a large CV/test gap, or depends on descriptors that do not make chemical sense.

## Question: Why does ROBERT care about y-shuffle?
The y-shuffle test checks whether the model still looks good after target values are randomized. If the model performs well with scrambled answers, the apparent performance may be accidental or overfit rather than chemically meaningful.

## Question: Why does ROBERT compare against predicting the mean?
The y-mean test asks whether the model is better than a very simple baseline. If the machine-learning model is not clearly better than predicting the average value, it may not be learning useful descriptor-target relationships.

## Question: What does one-hot mean?
In the one-hot test, nonzero descriptor values are converted to 1 and zero values remain 0. This checks whether the model is using actual descriptor magnitudes or mostly relying on presence/absence patterns.

## Question: Why is my test error worse than cross-validation?
A worse test error may mean the model is overfit, the test set is harder, the split is unstable, the dataset is small, outliers dominate the test set, or the test compounds are chemically different from the training compounds.

The next step is to compare CV and test metrics, inspect outliers, and check the y-value and chemical distribution of the test set.

## Question: What does high uncertainty mean?
High uncertainty means predictions vary substantially across repeated cross-validation refits. The model may be sensitive to the particular training points used. This often happens with small datasets, sparse chemical space, noisy y values, or weak descriptors.

## Question: What does sorted CV tell me?
Sorted CV checks behavior across the target-value range. It helps reveal whether the model struggles near low or high y values, which can be a sign of weak extrapolation or uneven target coverage.

## Question: Why did ROBERT remove many descriptors?
ROBERT removes descriptors to reduce redundancy, noise, and overfitting risk. It may remove highly correlated descriptors, duplicates, or descriptors that do not help model performance. A smaller descriptor set can be more interpretable, but it should still be checked against model performance and chemical meaning.

## Question: Is it bad if ROBERT kept only a few descriptors?
Not necessarily. A small descriptor set can be good if the model performs well, passes VERIFY tests, and the descriptors make chemical sense. It may be concerning if performance is weak or if the retained descriptors do not have a plausible connection to the target.

## Question: What is PFI?
PFI means permutation feature importance. ROBERT shuffles a descriptor and checks how much model performance worsens. If shuffling a descriptor hurts performance, that descriptor was important to the model.

## Question: What is SHAP?
SHAP estimates how descriptors contribute to individual predictions. It can help explain why a specific point was predicted high or low. SHAP is useful for interpretation but should not be treated as proof of causation.

## Question: What should I do if there are outliers?
Inspect the outliers carefully. They may be experimental errors, unusual chemistry, compounds outside the training space, or evidence that important descriptors are missing. Do not remove outliers automatically. First ask whether they are chemically meaningful.

## Question: What should I do if the model score is weak?
Start by identifying the limiting factor. Check VERIFY tests, CV/test gap, uncertainty, outliers, dataset size, y-value distribution, and descriptor relevance. Useful next actions may include adding datapoints, improving descriptors, checking data quality, or focusing on a narrower chemical domain.

## Question: What should I do if the model score is moderate?
A moderate score often means the model has some useful signal but also important caveats. It may be suitable for hypothesis generation or prioritization, but not for high-confidence prediction without further validation.

## Question: When should I add more data?
Add data when the dataset is small, the y-value range is sparse, uncertainty is high, outliers cluster in a region, or test performance is much worse than CV. Prioritize new datapoints in underrepresented chemical or target-value regions.

## Question: When should I improve descriptors?
Improve descriptors when VERIFY tests are weak, top descriptors are not chemically meaningful, predictions fail for a specific chemical class, or the current descriptors do not represent the mechanism or property being predicted.

## Question: Should I rerun ROBERT with a different split?
Only rerun with a different split when there is a clear reason, such as an unbalanced target distribution or a test set that is not representative. Do not use repeated reruns simply to find a better-looking score, because that can create selection bias.

## Question: What is the role of the LLM companion?
The companion should not replace ROBERT's calculations. It should explain ROBERT's existing outputs in plain language, connect related evidence, and help the user decide what to inspect next.

## Search keywords and aliases
FAQ, common questions, chemist explanation, why score, trust model, reliable model, weak model, moderate model, y shuffle, y-randomization, y mean, one hot, CV test gap, uncertainty, sorted CV, extrapolation, outliers, descriptors, PFI, SHAP, feature importance, next steps, improve model, rerun ROBERT, add data, improve descriptors.
