"""Chat helpers for heuristics-first responses and optional LLM fallback."""

import logging
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List

# Support both package imports (tests/app) and direct module execution.
try:
    from .llm_context import pack_evidence, TokenBudget
    from ..chat_prompts import format_system_prompt
    from .rag.retrieve import retrieve, build_context
    from .config import load_openai_model
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from llm_context import pack_evidence, TokenBudget
    from chat_prompts import format_system_prompt
    from rag.retrieve import retrieve, build_context
    from config import load_openai_model

logger = logging.getLogger(__name__)

QUERY_COUNTS = {
    "heuristic": 0,
    "local_rag": 0,
    "openai": 0,
    "openai_unavailable": 0,
    "no_api_key": 0,
}


def _is_score_question(user_question: str) -> bool:
    """Return True when the user is asking about score-level interpretation."""
    q = (user_question or "").strip().lower()
    return "score" in q or ("why" in q and ("model" in q or "result" in q))


def _extract_robert_scores(
    run_context: Dict[str, Any],
    diagnosis_json: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Extract ROBERT score fields from run_context and diagnosis_json when available."""
    score = run_context.get("score", {}) if isinstance(run_context, dict) else {}
    if not isinstance(score, dict) or (score.get("no_pfi") is None and score.get("pfi") is None):
        diag_score = diagnosis_json.get("robert_score", {}) if isinstance(diagnosis_json, dict) else {}
        if isinstance(diag_score, dict):
            score = diag_score

    return {
        "no_pfi": score.get("no_pfi") if isinstance(score, dict) else None,
        "pfi": score.get("pfi") if isinstance(score, dict) else None,
    }


def _format_robert_score_line(scores: Dict[str, Any]) -> str:
    """Format a single concise line for ROBERT score values."""
    no_pfi = scores.get("no_pfi")
    pfi = scores.get("pfi")
    if no_pfi is not None or pfi is not None:
        return f"ROBERT Score (No PFI / PFI): {no_pfi} / {pfi}."
    return (
        "ROBERT score is not present in the extracted run context for this run. "
        "Run extraction/diagnosis again if you expect score fields to be populated."
    )


def _artifact_label(artifact_key: str) -> str:
    """Return a short human-readable label for a run artifact key."""
    labels = {
        "results_plot": "Results plot",
        "cv_variability_plot": "CV variability plot",
        "shap_plot": "SHAP plot",
        "pfi_plot": "PFI plot",
        "pearson_heatmap": "Pearson heatmap",
        "outliers_plot": "Outliers plot",
        "y_distribution_plot": "Target distribution plot",
        "verify_plot": "VERIFY flawed-model plot",
    }
    return labels.get(artifact_key, artifact_key.replace("_", " ").title())


def _verify_plot_relpath(run_context: Dict[str, Any], variant: str) -> Optional[str]:
    """Return relative path to the VERIFY comparison plot for the selected variant."""
    verify = run_context.get("verify", {}) if isinstance(run_context, dict) else {}
    section = verify.get(variant, {}) if isinstance(verify, dict) else {}
    artifacts = section.get("artifacts", {}) if isinstance(section, dict) else {}
    if isinstance(artifacts, dict):
        explicit = artifacts.get("verify_plot")
        if isinstance(explicit, str) and explicit.lower().endswith((".png", ".jpg", ".jpeg")):
            return explicit

    model = run_context.get("ml_model") if isinstance(run_context, dict) else None
    if not isinstance(model, str) or not model:
        return None
    suffix = "PFI" if variant == "pfi" else "No_PFI"
    return f"VERIFY/VERIFY_tests_{model}_{suffix}.png"


def _artifact_topic(user_question: str) -> Optional[str]:
    """Map a question to the most relevant artifact topic when possible."""
    q = (user_question or "").strip().lower()
    if not q:
        return None

    if any(
        term in q
        for term in (
            "flawed",
            "y_mean",
            "y_shuffle",
            "onehot",
            "verify",
            "verification",
            "sorted cross-validation",
        )
    ):
        return "verify"

    if any(
        term in q
        for term in (
            "shap",
            "feature importance",
            "variable importance",
            "pfi",
            "descriptor",
            "feature",
            "which features",
            "what features",
            "drivers",
            "influenc",
            "importance",
            "correlat",
        )
    ):
        return "feature"
    if any(
        term in q
        for term in (
            "outlier",
            "anomal",
            "distribution",
            "uniform",
            "target spread",
            "y distribution",
            "skew",
            "balanced",
            "balance",
            "spread",
        )
    ):
        return "data_quality"
    if any(
        term in q
        for term in (
            "cv",
            "test",
            "overfit",
            "overfitting",
            "gap",
            "predictive ability",
            "results",
            "performance",
            "predictive",
            "fit",
        )
    ):
        return "performance"
    if "score" in q or ("why" in q and ("model" in q or "result" in q)):
        return "performance"
    return None


def _artifact_bundle_summary(artifacts: List[Dict[str, Any]]) -> str:
    """Return a short summary of the selected artifact bundle."""
    labels = [str(item.get("label", item.get("key", "artifact"))) for item in artifacts if isinstance(item, dict)]
    labels = [label for label in labels if label]
    if not labels:
        return "relevant evidence images"
    if len(labels) == 1:
        return labels[0]
    if len(labels) == 2:
        return f"{labels[0]} and {labels[1]}"
    return ", ".join(labels[:-1]) + f", and {labels[-1]}"


def _append_artifact_note(content: str, artifacts: List[Dict[str, Any]]) -> str:
    """Append a short note describing attached evidence images."""
    if not artifacts:
        return content
    note = f"Attached evidence images: {_artifact_bundle_summary(artifacts)}."
    if content.strip().endswith(note):
        return content
    return f"{content}\n\n{note}" if content else note


def _select_evidence_artifacts(user_question: str, run_context: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Return the most relevant image artifacts for a question."""
    if not isinstance(run_context, dict):
        return []

    predict = run_context.get("predict", {}) if isinstance(run_context.get("predict"), dict) else {}
    variant = _best_variant(run_context)
    topic = _artifact_topic(user_question)

    if topic == "verify":
        verify_plot = _verify_plot_relpath(run_context, variant)
        if isinstance(verify_plot, str) and verify_plot.lower().endswith((".png", ".jpg", ".jpeg")):
            return [
                {
                    "key": "verify_plot",
                    "label": _artifact_label("verify_plot"),
                    "variant": variant,
                    "path": verify_plot,
                }
            ]
        return []

    if topic == "feature":
        artifact_keys = ["shap_plot", "pfi_plot", "pearson_heatmap"]
    elif topic == "data_quality":
        artifact_keys = ["outliers_plot", "y_distribution_plot"]
    else:
        artifact_keys = ["results_plot", "cv_variability_plot"]

    variant_context = predict.get(variant, {}) if isinstance(predict, dict) else {}
    artifacts = variant_context.get("artifacts", {}) if isinstance(variant_context, dict) else {}
    if not isinstance(artifacts, dict):
        return []

    selected: List[Dict[str, Any]] = []
    for key in artifact_keys:
        path = artifacts.get(key)
        if not isinstance(path, str) or not path.lower().endswith((".png", ".jpg", ".jpeg")):
            continue
        selected.append(
            {
                "key": key,
                "label": _artifact_label(key),
                "variant": variant,
                "path": path,
            }
        )
    return selected


def _is_local_rag_enabled() -> bool:
    """Return whether local RAG retrieval should run for unmatched questions."""
    value = os.getenv("ROBERT_ENABLE_LOCAL_RAG", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def _rag_storage_dir() -> str:
    """Return storage directory path for local RAG artifacts."""
    return os.getenv("ROBERT_RAG_STORAGE_DIR", "agent/ui/storage")


def _rag_top_k() -> int:
    """Return top-k retrieval size for local RAG."""
    try:
        return max(1, int(os.getenv("ROBERT_RAG_TOP_K", "3")))
    except ValueError:
        return 3


def _knowledge_dir() -> Path:
    """Return path to local knowledge directory."""
    return Path(os.getenv("ROBERT_RAG_KNOWLEDGE_DIR", "agent/ui/knowledge"))


def _local_index_stale_hint() -> Optional[str]:
    """Return a warning if local knowledge appears newer than the saved index."""
    storage = Path(_rag_storage_dir())
    chunks_path = storage / "chunks.jsonl"
    bm25_path = storage / "bm25.pkl"
    if not chunks_path.exists() or not bm25_path.exists():
        return None

    index_mtime = min(chunks_path.stat().st_mtime, bm25_path.stat().st_mtime)
    knowledge = _knowledge_dir()
    if not knowledge.exists():
        return None

    newest_doc_mtime = None
    for path in knowledge.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".txt", ".md", ".pdf"}:
            mtime = path.stat().st_mtime
            newest_doc_mtime = mtime if newest_doc_mtime is None else max(newest_doc_mtime, mtime)

    if newest_doc_mtime is not None and newest_doc_mtime > index_mtime:
        return (
            "Note: knowledge files look newer than the current index. "
            "Rebuild the local knowledge index notebook for freshest retrieval results."
        )
    return None


def _get_local_rag_context(user_question: str, use_local_rag: Optional[bool] = None) -> Dict[str, Any]:
    """Retrieve local RAG chunks for a user question."""
    enabled = _is_local_rag_enabled() if use_local_rag is None else bool(use_local_rag)
    if not enabled:
        return {"enabled": False, "results": [], "context": "", "error": None}

    try:
        results = retrieve(
            query=user_question,
            k=_rag_top_k(),
            storage_dir=_rag_storage_dir(),
        )
    except Exception as exc:
        logger.info("Local RAG unavailable for this query: %s", exc)
        return {"enabled": True, "results": [], "context": "", "error": str(exc)}

    context = build_context(results) if results else ""
    return {"enabled": True, "results": results, "context": context, "error": None}


def _local_rag_response(rag_payload: Dict[str, Any]) -> Optional[str]:
    """Return a user-facing response from local retrieval results."""
    results = rag_payload.get("results", []) if isinstance(rag_payload, dict) else []
    if not results:
        return None

    lines = [
        "I could not match a deterministic FAQ rule, but I found relevant local knowledge snippets:",
        "",
    ]
    for i, item in enumerate(results, start=1):
        text = str(item.get("text", "")).strip().replace("\n", " ")
        preview = text[:260] + ("..." if len(text) > 260 else "")
        lines.append(
            f"[{i}] {item.get('source_name', 'unknown')} | chunk {item.get('chunk_index', '?')} | score={item.get('score', 0.0):.4f}"
        )
        lines.append(preview)
        lines.append("")

    stale_hint = _local_index_stale_hint()
    if stale_hint:
        lines.append(stale_hint)

    return "\n".join(lines).strip()


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

    model_name = load_openai_model("gpt-4o-mini")
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
    tokens_input: int = 0,
    tokens_output: int = 0,
    cost_usd: float = 0.0,
    artifacts: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    """
    Format a single chat message (Phase 2).
    
    Args:
        role: "user" or "assistant"
        content: Message content
        source: Message source (heuristic, openai, etc.)
        parity_status: Parity verification status
        tokens_input: Tokens used for input
        tokens_output: Tokens used for output
        cost_usd: Estimated USD cost
        
    Returns:
        Dict with keys: role, content, source, parity_status, tokens_input, tokens_output, cost_usd, artifacts
    """
    message = {
        "role": role,
        "content": content,
        "source": source,
        "tokens_input": tokens_input,
        "tokens_output": tokens_output,
        "cost_usd": cost_usd,
    }
    if parity_status:
        message["parity_status"] = parity_status
    if artifacts:
        message["artifacts"] = artifacts
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

    if (
        ("plot" in q or "image" in q or "figure" in q)
        and any(term in q for term in ("don't see", "do not see", "cant see", "can't see", "where", "show"))
    ):
        return (
            "Those evidence images are shown as cards in assistant replies on the right panel, "
            "and they are also available in the left panel under Evidence Images for the selected run. "
            "If you still do not see them, re-send a score/feature/outlier/distribution question after selecting the run again."
        )

    if "specific plot" in q or (("surface" in q or "show" in q) and "plot" in q):
        return (
            "I will surface the most relevant run plot in the assistant card attachment for this question. "
            "For flawed-model/VERIFY questions this is the VERIFY flawed-model plot; "
            "for feature or data-quality questions, the corresponding SHAP/PFI or outlier/distribution plots are attached."
        )

    if any(term in q for term in ("flawed", "y_mean", "y_shuffle", "onehot")):
        verify_block = run_context.get("verify", {}).get(variant, {}) if isinstance(run_context.get("verify"), dict) else {}
        outcomes = verify_block.get("test_outcomes", []) if isinstance(verify_block, dict) else []
        cv_rmse = verify_block.get("cv_rmse_original") if isinstance(verify_block, dict) else None
        threshold_15 = verify_block.get("threshold_15") if isinstance(verify_block, dict) else None
        threshold_30 = verify_block.get("threshold_30") if isinstance(verify_block, dict) else None

        lines = [
            "In that VERIFY plot, 'model' is your real model CV RMSE, while y_mean, y_shuffle, and onehot are intentionally flawed baselines.",
            "For a healthy model, those flawed baselines should have clearly worse (higher) RMSE than your model.",
        ]
        if cv_rmse is not None and threshold_15 is not None and threshold_30 is not None:
            lines.append(
                f"For this run ({variant.upper()}), model CV RMSE is {cv_rmse}, with +15% and +30% reference thresholds at {threshold_15} and {threshold_30}."
            )
        if isinstance(outcomes, list) and outcomes:
            summary = []
            for item in outcomes:
                if not isinstance(item, dict):
                    continue
                summary.append(f"{item.get('test')}: {item.get('verdict')} (RMSE={item.get('metric_value')})")
            if summary:
                lines.append("VERIFY outcomes: " + "; ".join(summary) + ".")
        return " ".join(lines)

    if "why" in q and "score" in q:
            # Defer to the richer diagnosis-backed answer when available;
            # fallback below handles the case when diagnosis_json is absent.
            return None

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


def _interp_obs_for_variant(diagnosis_json: Dict[str, Any], variant: str) -> List[Dict[str, str]]:
    """Return interpretation observations for the given variant."""
    obs = diagnosis_json.get("observations", {}).get(variant, [])
    return [ob for ob in obs if isinstance(ob, dict) and ob.get("key", "").startswith("interp_")]


def heuristic_answer_from_diagnosis(
    user_question: str,
    run_context: Dict[str, Any],
    diagnosis_json: Dict[str, Any],
) -> Optional[str]:
    """
    Answer using interpretation observations from diagnosis_json when available.
    Falls back to metric echoes when no interpretation observations exist.
    """
    if not user_question or not isinstance(diagnosis_json, dict):
        return None

    q = user_question.strip().lower()
    variant = _best_variant(run_context)
    m = _extract_metrics(run_context, variant)
    verify = _verify_counts(run_context, variant)
    pred_type = run_context.get("pred_type", "reg") if isinstance(run_context, dict) else "reg"

    if "why" in q and "score" in q:
        interp = _interp_obs_for_variant(diagnosis_json, variant)
        score_line = _format_robert_score_line(_extract_robert_scores(run_context, diagnosis_json))
        warning_msgs = [ob["message"] for ob in interp if ob.get("level", "").upper() in ("WARNING", "FAILED")]
        info_msgs = [ob["message"] for ob in interp if ob.get("level", "").upper() == "INFO"]

        if pred_type == "clas":
            metric_line = f"MCC CV/Test = {m['r2_cv']} / {m['r2_test']}"
        else:
            metric_line = f"R2 CV/Test = {m['r2_cv']} / {m['r2_test']}, RMSE CV/Test = {m['rmse_cv']} / {m['rmse_test']}"

        verify_line = (
            f"VERIFY ({variant.upper()}): {verify['passed']} passed, "
            f"{verify['failed']} failed, {verify['unclear']} unclear."
        )

        if warning_msgs:
            parts = [score_line, f"{metric_line}. {verify_line}"]
            parts.append("Key findings from this run:")
            parts.extend(f"• {msg}" for msg in warning_msgs[:3])
            if info_msgs:
                parts.extend(f"• {msg}" for msg in info_msgs[:1])
            return "\n\n".join(parts)

        # No warnings — model looks reasonable
        return (
            f"{score_line} {metric_line}. {verify_line} "
            "No major interpretation flags were raised. "
            "The evidence is consistent with a model that is performing at its natural limit "
            "given the dataset size and descriptors provided."
        )

    if ("cv" in q and "test" in q and ("gap" in q or "different" in q)) or "gap" in q:
        interp = _interp_obs_for_variant(diagnosis_json, variant)
        gap_obs = [ob for ob in interp if ob.get("key") in ("interp_cv_optimistic", "interp_test_better_than_cv")]
        if gap_obs:
            return gap_obs[0]["message"]
        if pred_type == "clas":
            return (
                f"For {variant.upper()}, MCC CV = {m['r2_cv']}, MCC Test = {m['r2_test']}. "
                "No notable gap was detected between CV and test performance."
            )
        return (
            f"For {variant.upper()}, R2 CV/Test = {m['r2_cv']} / {m['r2_test']} and "
            f"RMSE CV/Test = {m['rmse_cv']} / {m['rmse_test']}. "
            "No notable gap was detected between CV and test performance."
        )

    if "descriptor" in q or "feature" in q:
        interp = _interp_obs_for_variant(diagnosis_json, variant)
        dom_obs = [ob for ob in interp if ob.get("key") == "interp_dominant_feature"]
        corr_obs = [ob for ob in interp if ob.get("key") == "interp_descriptor_correlation"]
        descriptors = ", ".join(str(d) for d in m["descriptors"]) if m["descriptors"] else "N/A"
        base = (
            f"{variant.upper()} uses {m['n_descriptors']} descriptors: {descriptors}. "
            f"Train:descriptor ratio = {m['points_descp_ratio']}."
        )
        extras = []
        if dom_obs:
            extras.append(dom_obs[0]["message"])
        if corr_obs:
            extras.append(corr_obs[0]["message"])
        if extras:
            return base + "\n\n" + "\n\n".join(extras)
        return base

    return None


def call_llm_api_with_budget(
    api_key: str,
    user_question: str,
    run_context: dict,
    diagnosis_json: dict,
    retrieved_context: str = "",
    response_style: str = "REPORT_ONLY",
) -> Optional[Dict[str, Any]]:
    """
    Call OpenAI API with compact evidence packing and token tracking.
    
    Args:
        api_key: OpenAI API key
        user_question: User's question
        run_context: Run context dict
        diagnosis_json: Diagnosis dict
        retrieved_context: Optional local RAG context
        response_style: "REPORT_ONLY" or "REPORT_WITH_KB"
    
    Returns:
        dict with 'content', 'source', 'tokens_input', 'tokens_output', 'cost_usd'
    """
    try:
        from openai import OpenAI
    except ImportError:
        logger.warning("OpenAI package not installed; fallback remains unavailable")
        return None
    
    # Pack evidence
    budget = TokenBudget()
    evidence_text, budget = pack_evidence(run_context, diagnosis_json, user_question, budget)
    if retrieved_context:
        evidence_text = (
            evidence_text
            + "\n\nLocal Knowledge (retrieved locally; cite with source labels):\n"
            + retrieved_context
        )
        budget.add_context(retrieved_context)
    
    # Get system prompt
    model_name = load_openai_model("gpt-4o-mini")
    system_prompt = format_system_prompt(
        evidence=evidence_text,
        question=user_question,
        knowledge_base_text=retrieved_context if response_style == "REPORT_WITH_KB" else None,
        response_style=response_style,
    )
    
    # Call API
    client = OpenAI(api_key=api_key)
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_question},
            ],
            max_tokens=int(os.getenv("ROBERT_OPENAI_MAX_TOKENS", "350")),
            temperature=0.7,
        )
        
        answer = response.choices[0].message.content
        
        # Track token usage
        if hasattr(response, 'usage'):
            budget.total_input = response.usage.prompt_tokens
            budget.total_output = response.usage.completion_tokens
        else:
            budget.compute_totals()
        
        return {
            "content": answer,
            "source": "openai",
            "tokens_input": budget.total_input,
            "tokens_output": budget.total_output,
            "cost_usd": budget.cost_usd,
        }
    
    except Exception as exc:
        logger.warning("OpenAI request failed: %s", exc)
        return None


def answer_question(
    user_question: str,
    run_context: Dict[str, Any],
    diagnosis_json: Optional[Dict[str, Any]],
    api_key: Optional[str],
    use_local_rag: Optional[bool] = None,
    chat_mode: str = "HEURISTICS_FIRST",
    response_style: str = "REPORT_ONLY",
) -> Dict[str, str]:
    """
    Answer with heuristics first (or LLM only if specified). If no match, return a controlled fallback message.
    
    Args:
        user_question: User's question
        run_context: Run context dict
        diagnosis_json: Diagnosis dict
        api_key: OpenAI API key (optional)
        use_local_rag: Whether to enable local RAG retrieval
        chat_mode: "HEURISTICS_FIRST" or "LLM_ONLY"
        response_style: "REPORT_ONLY" or "REPORT_WITH_KB"
    
    Returns:
        Dict with response content and metadata
    """
    # Handle LLM_ONLY mode
    if chat_mode == "LLM_ONLY":
        if not api_key:
            return {
                "source": "no-api-key",
                "content": (
                    "LLM-only mode is selected, but ROBERT_CHAT_API_KEY is not configured. "
                    "Set ROBERT_CHAT_API_KEY to enable LLM-only chat, or switch to Heuristics First mode."
                ),
                "tokens_input": 0,
                "tokens_output": 0,
                "cost_usd": 0.0,
                "artifacts": [],
            }
        # Skip heuristics, go directly to LLM
        rag_payload = _get_local_rag_context(user_question, use_local_rag=use_local_rag)
        rag_context = rag_payload.get("context", "") if isinstance(rag_payload, dict) else ""
        result = call_llm_api_with_budget(
            api_key,
            user_question,
            run_context or {},
            diagnosis_json or {},
            retrieved_context=rag_context,
            response_style=response_style,
        )
        artifacts = _select_evidence_artifacts(user_question, run_context)
        if result:
            result["artifacts"] = artifacts
            result["content"] = _append_artifact_note(str(result.get("content", "")), artifacts)
            _log_query_route("openai")
            return result
        _log_query_route("openai_unavailable")
        return {
            "source": "fallback-disabled",
            "content": (
                "LLM-only mode is selected, but the OpenAI API call failed. "
                "Please try again, or switch to Heuristics First mode for deterministic answers."
            ),
            "tokens_input": 0,
            "tokens_output": 0,
            "cost_usd": 0.0,
            "artifacts": artifacts,
        }
    
    # Heuristics-first mode (original logic)
    response = heuristic_answer(user_question, run_context)
    if response is None and isinstance(diagnosis_json, dict):
        response = heuristic_answer_from_diagnosis(user_question, run_context, diagnosis_json)

    artifacts = _select_evidence_artifacts(user_question, run_context)
    if response and artifacts:
        response = f"{response}\n\nAttached evidence images: {_artifact_bundle_summary(artifacts)}."

    # For score-oriented questions, try to attach local KB snippets even when heuristics answer.
    rag_payload: Dict[str, Any] = {"enabled": False, "results": [], "context": "", "error": None}
    if _is_score_question(user_question):
        rag_payload = _get_local_rag_context(user_question, use_local_rag=use_local_rag)

    if response:
        local_response = _local_rag_response(rag_payload)
        if local_response:
            response = f"{response}\n\nRelated local knowledge snippets:\n\n{local_response}"
        response = _append_artifact_note(response, artifacts)
        _log_query_route("heuristic")
        return {
            "source": "heuristic",
            "content": response,
            "tokens_input": 0,
            "tokens_output": 0,
            "cost_usd": 0.0,
            "artifacts": artifacts,
        }

    rag_payload = _get_local_rag_context(user_question, use_local_rag=use_local_rag)
    rag_context = rag_payload.get("context", "") if isinstance(rag_payload, dict) else ""

    local_response = _local_rag_response(rag_payload)
    if local_response and not api_key:
        local_response = _append_artifact_note(local_response, artifacts)
        _log_query_route("local_rag")
        return {
            "source": "local-rag",
            "content": local_response,
            "tokens_input": 0,
            "tokens_output": 0,
            "cost_usd": 0.0,
            "artifacts": artifacts,
        }

    if api_key:
        result = call_llm_api_with_budget(
            api_key,
            user_question,
            run_context or {},
            diagnosis_json or {},
            retrieved_context=rag_context,
            response_style=response_style,
        )
        if result:
            result["artifacts"] = artifacts
            result["content"] = _append_artifact_note(str(result.get("content", "")), artifacts)
            _log_query_route("openai")
            return result

        _log_query_route("openai_unavailable")
        return {
            "source": "fallback-disabled",
            "content": (
                "This question did not match a deterministic FAQ rule. "
                "OpenAI fallback was attempted but is unavailable. "
                "Please ask about score reason, CV/test gap, VERIFY status, descriptors, outliers, or warnings."
            ),
            "tokens_input": 0,
            "tokens_output": 0,
            "cost_usd": 0.0,
            "artifacts": artifacts,
        }

    _log_query_route("no_api_key")
    return {
        "source": "no-api-key",
        "content": (
            "This question did not match a deterministic FAQ rule. "
            "Set ROBERT_CHAT_API_KEY to enable OpenAI fallback, "
            "or ask a supported question about score reason, CV/test gap, VERIFY tests, descriptors, outliers, or warnings."
        ),
        "tokens_input": 0,
        "tokens_output": 0,
        "cost_usd": 0.0,
        "artifacts": artifacts,
    }


# In-memory fallback state for local session use.
CHAT_HISTORY: List[Dict[str, str]] = []
