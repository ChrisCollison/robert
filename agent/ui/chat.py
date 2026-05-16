"""Chat helpers for heuristics-first responses and optional LLM fallback."""

import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


def call_llm_api(
    api_key: str,
    user_question: str,
    diagnostic_context: Dict[str, Any],
) -> Optional[str]:
    """
    Call LLM API with diagnostic context (Phase 2).
    
    Args:
        api_key: OpenAI API key (or other provider)
        user_question: User's question about their results
        diagnostic_context: Extracted diagnostic data from run_context.json
        
    Returns:
        LLM response string, or None if API call fails
        
    Raises:
        ValueError: If API key is invalid
        TimeoutError: If API call times out
        
    Note:
        - Implementation will inject diagnostic evidence into system prompt
        - API key is passed server-side only; never exposed to browser
        - Errors are caught and returned as user-friendly messages
    """
    # LLM fallback is optional and not enabled in this phase.
    raise NotImplementedError("LLM fallback is not enabled in this build")


def build_system_prompt(diagnostic_context: Dict[str, Any]) -> str:
    """
    Build system prompt with injected diagnostic evidence (Phase 2).
    
    Args:
        diagnostic_context: Parsed diagnostic data
        
    Returns:
        System prompt for LLM
        
    Example:
        "A user is analyzing their ROBERT ML workflow.
         Here is the diagnostic evidence:
         - Model: Random Forest
         - CV R²: 0.77
         - Test R²: 0.78
         
         User question: {user_question}
         
         Provide a helpful, evidence-based answer..."
    """
    # LLM fallback is optional and not enabled in this phase.
    raise NotImplementedError("LLM fallback is not enabled in this build")


def format_chat_message(role: str, content: str, source: str = "assistant") -> Dict[str, str]:
    """
    Format a single chat message (Phase 2).
    
    Args:
        role: "user" or "assistant"
        content: Message content
        
    Returns:
        Dict with keys: role, content
    """
    return {"role": role, "content": content, "source": source}


def _best_variant(run_context: Dict[str, Any]) -> str:
    """Pick the model variant with stronger test performance when available."""
    predict = run_context.get("predict", {}) if isinstance(run_context, dict) else {}
    no_pfi = predict.get("no_pfi", {}) if isinstance(predict, dict) else {}
    pfi = predict.get("pfi", {}) if isinstance(predict, dict) else {}

    no_pfi_r2 = no_pfi.get("r2_test") if isinstance(no_pfi, dict) else None
    pfi_r2 = pfi.get("r2_test") if isinstance(pfi, dict) else None

    if isinstance(pfi_r2, (int, float)) and isinstance(no_pfi_r2, (int, float)):
        return "pfi" if pfi_r2 >= no_pfi_r2 else "no_pfi"
    if isinstance(pfi_r2, (int, float)):
        return "pfi"
    return "no_pfi"


def _verify_counts(run_context: Dict[str, Any], variant: str) -> Dict[str, Any]:
    verify = run_context.get("verify", {}) if isinstance(run_context, dict) else {}
    v = verify.get(variant, {}) if isinstance(verify, dict) else {}
    return {
        "passed": v.get("passed_tests", "N/A"),
        "failed": v.get("failed_tests", "N/A"),
        "unclear": v.get("unclear_tests", "N/A"),
    }


def _extract_metrics(run_context: Dict[str, Any], variant: str) -> Dict[str, Any]:
    predict = run_context.get("predict", {}) if isinstance(run_context, dict) else {}
    p = predict.get(variant, {}) if isinstance(predict, dict) else {}
    return {
        "variant": variant,
        "r2_cv": p.get("r2_cv"),
        "r2_test": p.get("r2_test"),
        "rmse_cv": p.get("rmse_cv"),
        "rmse_test": p.get("rmse_test"),
        "n_train": p.get("n_train"),
        "n_test": p.get("n_test"),
        "n_descriptors": p.get("n_descriptors"),
        "descriptors": p.get("descriptors") or [],
        "points_descp_ratio": p.get("points_descp_ratio"),
        "train_outlier_pct": p.get("train_outlier_pct"),
        "test_outlier_pct": p.get("test_outlier_pct"),
        "warnings": p.get("warnings") or [],
    }


def _global_warnings(run_context: Dict[str, Any]) -> List[str]:
    warnings = run_context.get("parser_warnings", [])
    return warnings if isinstance(warnings, list) else []


def heuristic_answer(user_question: str, run_context: Dict[str, Any]) -> Optional[str]:
    """
    Return an evidence-grounded heuristic response when a supported FAQ pattern matches.
    """
    if not user_question or not isinstance(run_context, dict):
        return None

    q = user_question.strip().lower()
    variant = _best_variant(run_context)
    m = _extract_metrics(run_context, variant)
    verify = _verify_counts(run_context, variant)
    parser_warnings = _global_warnings(run_context)

    if "why" in q and "score" in q:
        return (
            f"Using the {variant.upper()} variant as reference: CV/Test R2 is {m['r2_cv']} / {m['r2_test']} "
            f"and CV/Test RMSE is {m['rmse_cv']} / {m['rmse_test']}. "
            f"VERIFY checks show passed={verify['passed']}, failed={verify['failed']}, unclear={verify['unclear']}. "
            "In this run, score limitations are more likely to come from data/representation constraints "
            "than from a failed VERIFY sanity check."
        )

    if "cv" in q and "test" in q and ("gap" in q or "different" in q):
        return (
            f"For {variant.upper()}, CV/Test R2 is {m['r2_cv']} / {m['r2_test']} and "
            f"CV/Test RMSE is {m['rmse_cv']} / {m['rmse_test']}. "
            "The CV and test metrics are close, so there is no strong evidence of split mismatch in this run."
        )

    if "verify" in q or "verification" in q or ("test" in q and "fail" in q):
        return (
            f"VERIFY summary ({variant.upper()}): passed={verify['passed']}, "
            f"failed={verify['failed']}, unclear={verify['unclear']}."
        )

    if "descriptor" in q or "feature" in q:
        descriptors = ", ".join(str(d) for d in m["descriptors"]) if m["descriptors"] else "N/A"
        return (
            f"{variant.upper()} uses {m['n_descriptors']} descriptors with train:descriptor ratio "
            f"{m['points_descp_ratio']}. Selected descriptors: {descriptors}."
        )

    if "outlier" in q:
        return (
            f"Outlier rates for {variant.upper()} are train={m['train_outlier_pct']}% and "
            f"test={m['test_outlier_pct']}%."
        )

    if "warning" in q or "missing" in q:
        run_warnings = [str(w) for w in m["warnings"]]
        all_warnings = run_warnings + parser_warnings
        if not all_warnings:
            return "No parser or model warnings were found in the extracted context for this run."
        return "Warnings in this run: " + " | ".join(all_warnings)

    return None


def answer_question(
    user_question: str,
    run_context: Dict[str, Any],
    diagnosis_json: Optional[Dict[str, Any]],
    api_key: Optional[str],
) -> Dict[str, str]:
    """
    Answer with heuristics first. If no match, return a controlled fallback message.
    """
    response = heuristic_answer(user_question, run_context)
    if response:
        return {"source": "heuristic", "content": response}

    # Explicitly avoid API use unless a real fallback implementation exists.
    if api_key:
        return {
            "source": "fallback-disabled",
            "content": (
                "This question did not match a deterministic FAQ rule yet. "
                "LLM fallback is intentionally disabled in this build. "
                "Please ask about score reason, CV/test gap, VERIFY status, descriptors, outliers, or warnings."
            ),
        }

    return {
        "source": "no-api-key",
        "content": (
            "This question did not match a deterministic FAQ rule. "
            "Set ROBERT_CHAT_API_KEY and enable fallback in a later phase, "
            "or ask a supported question about score reason, CV/test gap, VERIFY tests, descriptors, outliers, or warnings."
        ),
    }


# In-memory fallback state for local session use.
CHAT_HISTORY: List[Dict[str, str]] = []
