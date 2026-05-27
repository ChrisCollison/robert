# Feature selection, descriptor pruning, and feature importance

## Purpose of this knowledge card
Use this document when a user asks why ROBERT removed descriptors, what CURATE does, what PFI means, what SHAP means, whether descriptors are chemically meaningful, or whether too many or too few descriptors affected the score.

## Common user questions this document should help answer
- Why did ROBERT remove so many descriptors?
- What does CURATE do?
- Why does descriptor count matter?
- What is the correlation filter?
- What is RFECV?
- What is PFI?
- What is SHAP?
- Why are there No PFI and PFI models?
- Are my descriptors chemically meaningful?
- Did ROBERT over-prune my descriptors?

## Plain-English summary
ROBERT tries to reduce the descriptor set before and during modeling so the final model is simpler, more stable, and easier to interpret.

In chemistry datasets, there are often many descriptors that are redundant, noisy, or weakly related to the target. Removing them can improve interpretability and reduce overfitting. However, removing descriptors is not automatically good; the final model still needs to be checked for performance and chemical plausibility.

## CURATE module in plain language
CURATE cleans the input database before modeling. It can:

- Remove duplicated datapoints or descriptors.
- Remove highly correlated descriptors.
- Optionally remove descriptors with very low correlation to the target.
- Convert categorical variables into numeric or one-hot descriptors.
- Use RFECV to select a reduced descriptor set.

## Correlation filter
The correlation filter removes descriptors that are highly correlated with other descriptors. If two descriptors contain nearly the same information, keeping both may not help the model and may make interpretation harder.

Plain-English explanation: if two descriptors are telling the model almost the same thing, ROBERT may keep one and remove the other.

A large number of removed correlated descriptors may suggest:

- The descriptor set contains redundant information.
- Many descriptors come from related calculations.
- The initial descriptor set is much larger than needed.

## Low-correlation or noise filter
ROBERT can filter descriptors with very low correlation to the target. In some documentation this is described as disabled by default or suggested mainly for certain model types.

Plain-English explanation: this asks whether a descriptor has any obvious relationship with the target before modeling.

Caution: a descriptor with low simple correlation may still be useful in a nonlinear model or in combination with other descriptors. This filter should be interpreted carefully.

## Categorical descriptors
ROBERT can convert categorical variables into numerical or one-hot descriptors.

One-hot encoding creates separate 0/1 descriptors for categories. This can be useful, but it may also make the one-hot VERIFY test especially important, because the model might rely on category presence rather than continuous chemical values.

## RFECV
RFECV means recursive feature elimination with cross-validation. It tries to select a smaller set of descriptors that still supports good model performance.

Plain-English explanation: ROBERT tests descriptor subsets and removes descriptors that do not appear to help enough.

RFECV can improve interpretability, but it should be checked against performance and chemical plausibility.

## Descriptor-to-datapoint ratio
Too many descriptors for too few datapoints increases the risk of overfitting. ROBERT includes feature-selection steps partly to avoid models that are too complex for the available data.

Plain-English explanation: if the model has many possible explanations but only a few examples, it may find accidental patterns.

## PFI feature importance
PFI stands for permutation feature importance. It measures how much model performance worsens when a descriptor is randomly shuffled.

Plain-English explanation: if shuffling a descriptor makes the model worse, the model was relying on that descriptor.

PFI is useful for overall descriptor importance. It can help identify which descriptors are most important for model performance.

## SHAP feature importance
SHAP estimates how descriptors contribute to individual predictions.

Plain-English explanation: SHAP can help explain why a particular compound or reaction was predicted high or low.

SHAP is useful for local interpretation, but it should not be treated as proof of chemical causation.

## No PFI versus PFI models
ROBERT may generate two model tracks:

- No PFI: model using the selected descriptors without PFI filtering.
- PFI: model using descriptors retained after PFI-based filtering.

The PFI model is often simpler. Simpler models can be more interpretable and may generalize better, but the best choice depends on the actual metrics, score, and chemical plausibility.

## Chemical plausibility
Feature importance should be interpreted in light of chemistry. A descriptor may be statistically useful but chemically hard to justify. Conversely, a chemically meaningful descriptor may not appear important if the dataset is too small or if it is correlated with other descriptors.

Good explanation should ask:

- Do the top descriptors make chemical sense?
- Are important descriptors related to plausible mechanisms or properties?
- Are important descriptors artifacts of naming, category, scaffold, or data collection?
- Does the model rely on descriptors that would be available for future predictions?

## What the assistant should do with this information
When explaining descriptor behavior:

1. State how many descriptors were present before and after curation if available.
2. Identify whether descriptors were removed by correlation, RFECV, or PFI if available.
3. Explain why reducing descriptors can help.
4. Warn that descriptor removal should be checked against model performance.
5. Discuss chemical plausibility of top descriptors only when descriptor names and context are available.

## Useful next actions for users
- Inspect the curated CSV to see which descriptors remain.
- Compare No PFI and PFI model performance.
- Review top SHAP and PFI descriptors.
- Check whether retained descriptors are chemically meaningful.
- Add descriptors that better represent the mechanism or property.
- Remove descriptors that leak target information or encode experimental artifacts.
- Add more datapoints if descriptor count remains high relative to dataset size.

## Search keywords and aliases
CURATE, curation, descriptors, features, feature selection, descriptor pruning, removed descriptors, correlated descriptors, correlation filter, thres_x, thres_y, noise filter, duplicates, categorical, one-hot encoding, RFECV, recursive feature elimination, descriptor-to-datapoint ratio, too many descriptors, too few descriptors, PFI, permutation feature importance, SHAP, feature importance, descriptor importance, chemical plausibility, No PFI, PFI model, model interpretability.
