"""Guided FAQ configuration for run-specific ROBERT UI questions."""

from typing import Any, Dict, List, Optional

FAQ_CATEGORIES: List[Dict[str, str]] = [
    {"id": "summary", "label": "Summary and next steps"},
    {"id": "dataset", "label": "Dataset and features"},
    {"id": "reliability", "label": "Model reliability"},
    {"id": "warnings", "label": "Warnings and diagnostics"},
    {"id": "interpretation", "label": "Feature importance and interpretation"},
    {"id": "transparency", "label": "Transparency and reproducibility"},
]

FAQ_ITEMS: List[Dict[str, Any]] = [
    {
        "id": "why_robert_score",
        "label": "Why did I get this ROBERT score?",
        "category": "summary",
        "priority": "high",
        "starter": True,
        "requires_all": ["score_components", "warnings", "metrics"],
        "requires_any": ["outliers", "y_distribution", "descriptor_counts"],
        "rag_tags": ["ROBERT score", "model reliability", "warnings"],
        "prompt_template": "Use the specific score, score components, warnings, CV/test metrics, outliers, y-distribution, and descriptor counts. Explain the main reasons this run received its score. Do not give a generic score explanation without citing run-specific values.",
        "fallback_behavior": "If score evidence is incomplete, name the missing evidence explicitly and keep the answer diagnostic rather than generic.",
    },
    {
        "id": "main_takeaway",
        "label": "What is the main takeaway from this report?",
        "category": "summary",
        "priority": "high",
        "starter": True,
        "requires_all": ["metrics", "warnings"],
        "requires_any": ["score_components", "descriptor_counts"],
        "rag_tags": ["report summary", "model usefulness", "next steps"],
        "prompt_template": "Identify the preferred model, its score, model type, descriptor count, key metrics, warnings, and limitations. End with a clear bottom-line recommendation for this run.",
        "fallback_behavior": "If model-comparison evidence is incomplete, say which parts are missing before giving the best supported takeaway.",
    },
    {
        "id": "trust_pfi_vs_no_pfi",
        "label": "Should I trust the PFI or No PFI model more?",
        "category": "summary",
        "priority": "high",
        "starter": True,
        "requires_all": ["score_components", "metrics", "descriptor_counts"],
        "requires_any": ["warnings", "outliers"],
        "rag_tags": ["PFI", "No PFI", "model comparison"],
        "prompt_template": "Compare the PFI and No PFI models using their scores, model types, descriptor counts, CV metrics, test metrics, warnings, and outlier behavior. Recommend which model should be interpreted first and explain why.",
        "fallback_behavior": "If one branch is missing, state that explicitly and only compare what is actually available.",
    },
    {
        "id": "what_happened_to_features",
        "label": "What happened to my original features?",
        "category": "dataset",
        "priority": "high",
        "starter": True,
        "requires_all": ["dataset_profile", "descriptor_counts"],
        "requires_any": ["column_roles", "correlations"],
        "rag_tags": ["feature reduction", "curation", "descriptor selection"],
        "prompt_template": "Use dataset_profile.json to identify the original candidate descriptor count and column roles. Use ROBERT evidence to identify the final No PFI and PFI descriptor counts. Explain how much the feature set changed and whether that change is likely helpful or concerning.",
        "fallback_behavior": "If the original feature inventory is unavailable, say so and only describe the final descriptor counts that are present.",
    },
    {
        "id": "why_fewer_descriptors",
        "label": "Why did ROBERT use fewer descriptors than I provided?",
        "category": "dataset",
        "priority": "high",
        "starter": True,
        "requires_all": ["dataset_profile", "descriptor_counts"],
        "requires_any": ["correlations", "column_roles"],
        "rag_tags": ["descriptor burden", "correlation filtering", "PFI"],
        "prompt_template": "Compare the original descriptor count from dataset_profile.json with the final descriptor counts from ROBERT. Mention correlation filtering, curation, and PFI only when supported by run evidence. Explain this in chemist-facing language.",
        "fallback_behavior": "If the original descriptor count is missing, say so explicitly before explaining the final descriptor burden.",
    },
    {
        "id": "cv_test_meaning",
        "label": "What do cross-validation and test-set results tell me?",
        "category": "reliability",
        "priority": "high",
        "starter": True,
        "requires_all": ["metrics", "split_info"],
        "requires_any": ["score_components"],
        "rag_tags": ["cross-validation", "test set", "overfitting"],
        "prompt_template": "Use the specific CV and test R2, MAE, RMSE, scaled RMSE, and train/test split. Explain whether the CV and test results are consistent for this run. Warn if the test set is very small.",
        "fallback_behavior": "If the split details are missing, explain the available metrics and state that split interpretation is limited.",
    },
    {
        "id": "repeated_cv_meaning",
        "label": "What does 10 repeats of 5-fold cross-validation mean?",
        "category": "transparency",
        "priority": "medium",
        "starter": False,
        "requires_all": ["transparency"],
        "requires_any": ["split_info"],
        "rag_tags": ["kfold", "repeat_kfolds", "cross-validation"],
        "prompt_template": "Use the run's kfold and repeat_kfolds settings from the transparency section. Explain what this means for the number of training/validation points in this dataset when possible. State when the exact repeat mechanism should be verified from ROBERT code if it is not directly exposed.",
        "fallback_behavior": "If transparency settings are missing, say so and answer only at the conceptual level.",
    },
    {
        "id": "y_distribution_warning",
        "label": "What does the y-distribution warning mean?",
        "category": "warnings",
        "priority": "medium",
        "starter": False,
        "requires_all": ["y_distribution"],
        "requires_any": ["dataset_profile", "target_distribution"],
        "rag_tags": ["y distribution", "target range", "underrepresented regions"],
        "prompt_template": "Use the report's y-distribution warning and dataset_profile target distribution if available. Identify underrepresented regions and recommend adding datapoints there before over-interpreting predictions.",
        "fallback_behavior": "If the report does not expose a y-distribution warning, say so explicitly and only discuss the target distribution that is available.",
    },
    {
        "id": "extrapolation_meaning",
        "label": "What does extrapolation mean in this report?",
        "category": "warnings",
        "priority": "medium",
        "starter": False,
        "requires_all": ["extrapolation"],
        "requires_any": ["y_distribution", "metrics"],
        "rag_tags": ["extrapolation", "sorted CV", "target range"],
        "prompt_template": "Use the specific extrapolation or sorted-CV values and score contribution. Explain whether the model appears stable across the target range, and connect this to y-distribution and dataset size.",
        "fallback_behavior": "If extrapolation evidence is absent, say so rather than inferring it from unrelated metrics.",
    },
    {
        "id": "error_bars_sd",
        "label": "What do the error bars or standard deviation section mean?",
        "category": "warnings",
        "priority": "medium",
        "starter": False,
        "requires_all": ["standard_deviation"],
        "requires_any": ["target_distribution"],
        "rag_tags": ["standard deviation", "error bars", "prediction stability"],
        "prompt_template": "Use the report's average SD values and percentage of y-range. Explain what the percentage means relative to the target-property range. Warn that low variation supports stability but does not prove chemical accuracy.",
        "fallback_behavior": "If SD evidence is missing, say so explicitly and avoid inventing a stability conclusion.",
    },
    {
        "id": "outlier_analysis",
        "label": "What does the outlier analysis tell me?",
        "category": "warnings",
        "priority": "medium",
        "starter": False,
        "requires_all": ["outliers"],
        "requires_any": ["metrics"],
        "rag_tags": ["outliers", "prediction errors", "data quality"],
        "prompt_template": "Use the specific outlier counts, split location, molecule names or IDs if available, and SD values. Recommend inspecting outliers before removing them. Do not recommend deletion unless there is evidence of an error.",
        "fallback_behavior": "If only partial outlier evidence is available, state exactly what is available and what is not.",
    },
    {
        "id": "descriptor_meaning",
        "label": "Are the selected descriptors chemically meaningful?",
        "category": "interpretation",
        "priority": "medium",
        "starter": False,
        "requires_all": ["descriptor_counts"],
        "requires_any": ["feature_importance", "descriptor_inventory"],
        "rag_tags": ["descriptor meaning", "feature importance", "chemical interpretation"],
        "prompt_template": "Use the descriptors listed in the report and dataset profile. Explain their likely role only if definitions or reliable descriptor-family information are available. If not, say that the descriptor name suggests a possible interpretation but should be verified.",
        "fallback_behavior": "If descriptor definitions are not available, say so clearly and avoid overclaiming chemistry.",
    },
    {
        "id": "interpret_shap",
        "label": "How should I interpret a SHAP plot?",
        "category": "interpretation",
        "priority": "medium",
        "starter": False,
        "requires_all": ["feature_importance"],
        "requires_any": ["descriptor_counts"],
        "rag_tags": ["SHAP", "feature importance", "model interpretation"],
        "prompt_template": "Use the specific SHAP features and directions if available. Explain the plot in plain language. Do not infer chemistry beyond the evidence.",
        "fallback_behavior": "If a SHAP plot is not available for this run, say so explicitly and explain SHAP only as general background.",
    },
    {
        "id": "pfi_feature_difference",
        "label": "Why might a PFI-selected feature not appear important in the No PFI model?",
        "category": "interpretation",
        "priority": "medium",
        "starter": False,
        "requires_all": ["feature_importance"],
        "requires_any": ["correlations", "descriptor_counts"],
        "rag_tags": ["PFI", "feature importance", "correlated descriptors"],
        "prompt_template": "Compare the No PFI and PFI feature-importance lists. Check whether the descriptor may be correlated with others using dataset_profile correlation summary. Explain the model-context dependence of feature importance.",
        "fallback_behavior": "If one importance list is missing, state that clearly instead of inferring the comparison.",
    },
    {
        "id": "model_screening_for_chemist",
        "label": "Can you explain the model screening analysis for a chemist?",
        "category": "reliability",
        "priority": "medium",
        "starter": False,
        "requires_all": ["model_screening"],
        "requires_any": ["metrics", "score_components"],
        "rag_tags": ["model screening", "model selection", "hyperparameters"],
        "prompt_template": "Use the model-screening section and extracted model candidates if available. Explain which model was selected, what alternatives were considered if available, and why the selected model is likely preferred. Avoid unnecessary ML jargon.",
        "fallback_behavior": "If candidate models are not exposed in the extracted evidence, say so rather than implying a full screening table.",
    },
    {
        "id": "transparency_section",
        "label": "What do I need to know from the transparency section?",
        "category": "transparency",
        "priority": "medium",
        "starter": False,
        "requires_all": ["transparency"],
        "requires_any": ["reproducibility"],
        "rag_tags": ["transparency", "reproducibility", "audit trail"],
        "prompt_template": "Summarize the transparency section for this specific run. Separate 'important for interpretation' from 'important for reproducibility'. Explain settings only at a high level unless the user asks for more.",
        "fallback_behavior": "If transparency metadata is incomplete, explain only the settings that are actually present.",
    },
    {
        "id": "predict_new_molecules",
        "label": "Can I use this model to predict new molecules?",
        "category": "summary",
        "priority": "medium",
        "starter": False,
        "requires_all": ["score_components", "metrics"],
        "requires_any": ["warnings", "y_distribution", "outliers"],
        "rag_tags": ["applicability", "new molecules", "screening"],
        "prompt_template": "Use this run's score, warnings, dataset size, descriptor set, y-range, and outlier or extrapolation analysis. Give a specific recommendation about whether the model is suitable for screening, prioritization, or quantitative prediction.",
        "fallback_behavior": "If applicability evidence is partial, make that limitation explicit in the recommendation.",
    },
    {
        "id": "improve_model_next",
        "label": "What should I do next to improve the model?",
        "category": "summary",
        "priority": "high",
        "starter": False,
        "requires_all": ["warnings", "metrics"],
        "requires_any": ["outliers", "y_distribution", "descriptor_counts"],
        "rag_tags": ["improve model", "next steps", "data collection"],
        "prompt_template": "Use the specific warnings, y-distribution, outliers, score components, descriptor counts, and CV/test behavior to recommend 1 to 3 concrete next actions. Do not provide a generic laundry list.",
        "fallback_behavior": "If the limiting evidence is incomplete, say which limitations are confirmed and which are still uncertain.",
    },
]

FAQ_BY_ID: Dict[str, Dict[str, Any]] = {item["id"]: item for item in FAQ_ITEMS}
STARTER_FAQ_IDS: List[str] = [item["id"] for item in FAQ_ITEMS if item.get("starter")]


def get_faq_item(faq_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not faq_id:
        return None
    return FAQ_BY_ID.get(faq_id)


def get_starter_items() -> List[Dict[str, Any]]:
    return [FAQ_BY_ID[item_id] for item_id in STARTER_FAQ_IDS if item_id in FAQ_BY_ID]


def get_category_options(include_starters: bool = False) -> List[Dict[str, Any]]:
    grouped: List[Dict[str, Any]] = []
    for category in FAQ_CATEGORIES:
        options = []
        for item in FAQ_ITEMS:
            if item.get("category") != category["id"]:
                continue
            if not include_starters and item.get("starter"):
                continue
            options.append({"label": item["label"], "value": item["id"]})
        if options:
            grouped.append({
                "id": category["id"],
                "label": category["label"],
                "options": options,
            })
    return grouped
