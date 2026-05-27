# VERIFY tests

## Purpose of this knowledge card
Use this document when a user asks about VERIFY, y-mean, y-shuffle, one-hot tests, flawed models, failed verification tests, unclear verification tests, or whether the model is learning real signal.

## Common user questions this document should help answer
- What does VERIFY do?
- Why did my VERIFY test fail?
- What does y-shuffle mean?
- What does a failed y-shuffle test mean?
- What is the y-mean test?
- What is the one-hot test?
- Why does ROBERT compare my model to flawed models?
- Does a failed VERIFY test mean my model is useless?
- What should I do if VERIFY is unclear?

## Plain-English summary
VERIFY is ROBERT's sanity-check step. It asks whether a model that appears to predict well might actually be relying on weak, accidental, or misleading patterns.

VERIFY is important because a model can look good by normal metrics but still fail to learn meaningful chemical relationships. The VERIFY tests compare the real model against intentionally flawed or simplified versions of the problem.

## Official ROBERT behavior
The VERIFY module is run after GENERATE. It uses the model and data from the GENERATE folder. It performs tests including:

1. y-mean test.
2. y-shuffle test.
3. one-hot test.

The documentation describes pass thresholds using percentage differences in error or classification performance relative to the original model. Results can be interpreted as passed, unclear, or failed.

## y-mean test

### What ROBERT does
For regression, the y-mean test compares the model to a simple predictor that always predicts the mean of the measured y values. For classification, it uses the most common class.

### Plain-English meaning
This asks: is the machine-learning model doing better than a very simple baseline?

If the real model is not clearly better than predicting the average, then the model may not be extracting useful structure from the descriptors.

### Why it matters
A model should beat a simple baseline. If it cannot, the dataset may have weak signal, too much noise, too few datapoints, or descriptors that do not explain the target.

### What a poor result may suggest
- The target is hard to predict from the available descriptors.
- The dataset is too small or noisy.
- Important chemistry is missing from the descriptors.
- The y values do not vary enough to support a meaningful model.

## y-shuffle test

### What ROBERT does
The y-shuffle test randomly shuffles the measured y values and evaluates whether the model still appears to perform well.

### Plain-English meaning
This asks: if the answers are scrambled, does the model still look good?

If the model still performs well after the y values are shuffled, then the apparent model quality may be suspicious.

### Why it matters
A good model should depend on the real relationship between descriptors and target values. If performance remains strong after target values are randomized, the model may be overfitted or may be benefiting from accidental structure in the dataset.

### What a poor result may suggest
- The model may be overfitted.
- The dataset may be too small to distinguish real signal from chance.
- The split may be too easy or unrepresentative.
- The descriptors may encode grouping patterns that accidentally match the target.

## one-hot test

### What ROBERT does
The one-hot test replaces descriptor values with 0s and 1s. If a descriptor value is zero, it stays zero. If it is nonzero, it becomes one.

### Plain-English meaning
This asks: does the model care about the actual descriptor values, or only whether something is present or absent?

### Why it matters
For many chemistry models, the actual magnitude of descriptor values should matter. If a one-hot version performs similarly to the original, the model may be learning presence/absence patterns rather than meaningful quantitative chemistry.

### Example interpretation
In a reaction dataset with many columns indicating whether a reagent, ligand, solvent, or condition was used, a model may rely on whether a component appears at all rather than on its chemical property value.

### What a poor result may suggest
- The model may be driven by categorical presence/absence patterns.
- The descriptor values may not be adding meaningful information.
- The dataset may contain hidden grouping or repeated scaffold effects.
- The user may need better quantitative descriptors.

## Passed, unclear, and failed results

### Passed
A passed VERIFY test means the real model behaves better than the flawed comparison in the expected way. This supports confidence in the model.

### Unclear
An unclear result means the evidence is mixed. The model may contain signal, but the test did not strongly confirm it. The result should be interpreted cautiously and in combination with CV/test metrics, dataset size, and outliers.

### Failed
A failed result means the flawed or simplified comparison performed too similarly to the real model. This does not automatically prove the model is useless, but it is a warning that the model may not be learning the intended chemical relationship.

## How VERIFY affects the ROBERT score
VERIFY results are part of the ROBERT score. Passed tests do not penalize the model. Unclear or failed tests can reduce the score because they suggest the model's predictive ability may be less trustworthy.

## How to explain this to a chemist
VERIFY is like asking whether the model passes basic scientific sanity checks. It is not enough for the model to produce low error. ROBERT also asks whether the model beats simple or intentionally flawed alternatives.

## What the assistant should do with this information
When explaining a specific run:

1. State which VERIFY tests passed, failed, or were unclear.
2. Explain each failed or unclear test in plain language.
3. Connect the test to possible causes, but do not overstate certainty.
4. Use the actual run metrics and flags when available.
5. Suggest targeted next actions.

## Useful next actions for users
- Compare the real model's error to the y-mean and y-shuffle errors.
- Check whether the dataset is very small.
- Inspect whether descriptors are chemically meaningful.
- Look for repeated scaffolds, duplicate-like entries, or hidden categories.
- Review whether the split strategy is appropriate.
- Add datapoints in sparse target-value regions.
- Add descriptors that better represent the mechanism or property being predicted.

## Search keywords and aliases
VERIFY, verify tests, verification, failed VERIFY, unclear VERIFY, y-mean, ymean, mean test, baseline model, y-shuffle, y shuffle, y-randomization, shuffled targets, random y, one-hot, onehot, binary descriptors, flawed model, sanity check, overfitting, underfitting, weak signal, spurious correlation, model validity, model trust.
