"""
ROBERT Agent Chat Prompts (Phase 2).

System prompts and context templates for LLM integration.

These prompts will be injected with evidence from diagnostic outputs
(run_context.json, diagnosis.json) to help the LLM provide accurate,
evidence-based explanations of ROBERT scores.

Currently: STUB - to be implemented in Phase 2
"""


SYSTEM_PROMPT_TEMPLATE = """
You are an expert assistant helping chemists understand their ROBERT machine learning workflow results.

ROBERT is an automated ML tool that builds and evaluates regression or classification models on chemical data.

User's dataset: {dataset_name}
Prediction type: {pred_type}
Best model: {ml_model}

DIAGNOSTIC EVIDENCE:
{diagnostic_evidence}

Your role:
1. Explain the ROBERT score in plain language (not technical jargon)
2. Reference specific metrics and evidence (from above)
3. Identify limiting factors and suggest improvements
4. Distinguish between:
   - Model quality issues (poor hyperparameters, wrong algorithm)
   - Dataset issues (too small, noisy, unbalanced)
   - Descriptor issues (irrelevant features, missing chemistry)
   - Data split issues (training/test mismatch)

Be concise, evidence-based, and helpful.
"""


DIAGNOSIS_EVIDENCE_TEMPLATE = """
Model Performance:
- CV R²: {cv_r2}
- Test R²: {test_r2}
- CV-Test Gap: {cv_test_gap}

Verification Tests:
- Passed: {verify_passed}
- Failed: {verify_failed}
- Unclear: {verify_unclear}

Feature Curation:
- Initial descriptors: {initial_descriptors}
- Final descriptors: {final_descriptors}

Dataset:
- Train/CV/Test split: {train_test_split}
- Outliers: {outlier_count}

Diagnostic Flags:
{diagnostic_flags}
"""


FOLLOW_UP_SUGGESTIONS = [
    "Why is my model performance low?",
    "What's causing the gap between CV and test results?",
    "Are my descriptors relevant to the chemistry?",
    "Should I add more data?",
    "What are the most important features?",
    "Did any verification tests fail?",
    "How can I improve my score?",
]
