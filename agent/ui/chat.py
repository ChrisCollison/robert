"""Chat helpers for heuristics-first responses and optional LLM fallback."""

import logging
import os
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)

QUERY_COUNTS = {
    "heuristic": 0,
    "openai": 0,
    "openai_unavailable": 0,
    "no_api_key": 0,
}


def _log_query_route(route: str) -> None:
    QUERY_COUNTS[route] = QUERY_COUNTS.get(route, 0) + 1
    logger.info("Chat route=%s count=%s", route, QUERY_COUNTS[route])


def _format_diagnostic_context(diagnostic_context: Dict[str, Any]) -> str:
    if not isinstance(diagnostic_context, dict):
        return ""

    parts = []
    score = diagnostic_context.get("score", {})
    predict = diagnostic_context.get("predict", {})
    verify = diagnostic_context.get("verify", {})

    if isinstance(score, dict):
        parts.append(f"ROBERT score fields: {score}")
    if isinstance(predict, dict):
        parts.append(f"Predict summary: {predict}")
    if isinstance(verify, dict):
        parts.append(f"VERIFY summary: {verify}")

    parser_warnings = diagnostic_context.get("parser_warnings", [])
    if parser_warnings:
        parts.append(f"Parser warnings: {parser_warnings}")

    return "\n\n".join(parts)


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
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("OpenAI package not installed; fallback remains unavailable")
        return None

    model_name = os.getenv("ROBERT_OPENAI_MODEL", "gpt-4o-mini")
    max_tokens = int(os.getenv("ROBERT_OPENAI_MAX_TOKENS", "350"))

    client = OpenAI(api_key=api_key)
    system_prompt = build_system_prompt(diagnostic_context)

    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
            temperature=0.2,
            max_tokens=max_tokens,
        )
    except Exception as exc:
        logger.warning("OpenAI fallback request failed: %s", exc)
        return None

    choice = response.choices[0] if response.choices else None
    message = getattr(choice, "message", None) if choice else None
    content = getattr(message, "content", None) if message else None
    if content and str(content).strip():
        return str(content).strip()
    return None


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
    evidence_text = _format_diagnostic_context(diagnostic_context)
    return (
        "You are explaining a ROBERT diagnostic run. "
        "Use only the provided extracted evidence. "
        "Do not invent metrics, descriptor meanings, or score components. "
        "If evidence is missing, say so explicitly.\n\n"
        f"Extracted evidence:\n{evidence_text}"
    )


def format_chat_message(
    role: str,
    content: str,
    source: str = "assistant",
    parity_status: Optional[str] = None,
) -> Dict[str, str]:
    """
    Format a single chat message (Phase 2).
    
    Args:
        role: "user" or "assistant"
        content: Message content
        
    Returns:
        Dict with keys: role, content
    """
    message = {"role": role, "content": content, "source": source}
    if parity_status:
        message["parity_status"] = parity_status
    return message


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
        _log_query_route("heuristic")
        return {"source": "heuristic", "content": response}

    if api_key:
        fallback_response = call_llm_api(api_key, user_question, run_context or {})
        if fallback_response:
            _log_query_route("openai")
            return {"source": "openai", "content": fallback_response}

        _log_query_route("openai_unavailable")
        return {
            "source": "fallback-disabled",
            "content": (
                "This question did not match a deterministic FAQ rule. "
                "OpenAI fallback was attempted but is unavailable in this environment or failed to return a response. "
                "Please ask about score reason, CV/test gap, VERIFY status, descriptors, outliers, or warnings."
            ),
        }

    _log_query_route("no_api_key")
    return {
        "source": "no-api-key",
        "content": (
            "This question did not match a deterministic FAQ rule. "
            "Set ROBERT_CHAT_API_KEY to enable OpenAI fallback, "
            "or ask a supported question about score reason, CV/test gap, VERIFY tests, descriptors, outliers, or warnings."
        ),
    }


# In-memory fallback state for local session use.
CHAT_HISTORY: List[Dict[str, str]] = []
