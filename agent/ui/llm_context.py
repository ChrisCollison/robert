"""
Compact evidence packer and token counting for OpenAI requests.

Converts extracted run_context.json and diagnosis.json into a slim,
token-efficient context payload for the OpenAI API.

Also tracks token usage and estimated costs.
"""

import json
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

# Token estimates (rough, for gpt-4o-mini)
# Actual token count requires tiktoken; these are conservative estimates
TOKENS_PER_QUESTION = 50  # typical chemist question
TOKENS_PER_RESPONSE = 250  # typical OpenAI response
TOKENS_SYSTEM_PROMPT = 600  # instruction profile

# Pricing (gpt-4o-mini as of May 2026)
# Input: $0.15 per 1M tokens, Output: $0.60 per 1M tokens
PRICE_INPUT_PER_1M = 0.15
PRICE_OUTPUT_PER_1M = 0.60


class TokenBudget:
    """Track tokens and cost for a single request-response cycle."""
    
    def __init__(self):
        self.system_tokens = TOKENS_SYSTEM_PROMPT
        self.context_tokens = 0
        self.question_tokens = TOKENS_PER_QUESTION
        self.response_tokens = 0
        self.total_input = 0
        self.total_output = 0
        self.cost_usd = 0.0
    
    def add_context(self, text: str):
        """Estimate tokens from context text (rough: 1 token per 4 chars)."""
        self.context_tokens += len(text) // 4
    
    def set_response_tokens(self, tokens: int):
        """Set actual response token count if available."""
        self.response_tokens = tokens
    
    def compute_totals(self):
        """Compute total tokens and estimated cost."""
        self.total_input = self.system_tokens + self.context_tokens + self.question_tokens
        self.total_output = self.response_tokens or TOKENS_PER_RESPONSE
        
        input_cost = (self.total_input / 1e6) * PRICE_INPUT_PER_1M
        output_cost = (self.total_output / 1e6) * PRICE_OUTPUT_PER_1M
        self.cost_usd = input_cost + output_cost
    
    def summary(self) -> str:
        """Return a short summary for UI display."""
        self.compute_totals()
        return (
            f"Tokens: {self.total_input} in, {self.total_output} out | "
            f"Est. cost: ${self.cost_usd:.4f}"
        )


def pack_evidence(
    run_context: Dict[str, Any],
    diagnosis_json: Dict[str, Any],
    question: str,
    budget: Optional[TokenBudget] = None,
) -> Tuple[str, TokenBudget]:
    """
    Pack run_context and diagnosis_json into a compact evidence summary.
    
    Args:
        run_context: Extracted run context (from extract_context.ipynb)
        diagnosis_json: Diagnosis output (from diagnose_score.ipynb)
        question: User's question
        budget: Optional TokenBudget to track usage
        
    Returns:
        Tuple of (evidence_text, updated_budget)
    """
    if budget is None:
        budget = TokenBudget()
    
    lines = []
    
    # Dataset summary
    dataset_name = run_context.get("dataset_csv", "unknown")
    pred_type = run_context.get("pred_type", "unknown")
    ml_model = run_context.get("ml_model", "unknown")
    
    lines.append(f"Dataset: {dataset_name}")
    lines.append(f"Type: {pred_type} (model: {ml_model})")
    lines.append("")
    
    # Metrics summary (pick best variant by test performance)
    best_variant = "pfi"  # Default to PFI if available
    predict_no_pfi = run_context.get("predict", {}).get("no_pfi", {})
    predict_pfi = run_context.get("predict", {}).get("pfi", {})
    
    if predict_pfi.get("r2_test") is None and predict_no_pfi.get("r2_test") is not None:
        best_variant = "no_pfi"
    
    p = run_context.get("predict", {}).get(best_variant, {})
    v = run_context.get("verify", {}).get(best_variant, {})
    
    lines.append("Performance (primary variant):")
    if pred_type == "reg":
        lines.append(f"  CV R²: {p.get('r2_cv')}, Test R²: {p.get('r2_test')}")
        lines.append(f"  CV RMSE: {p.get('rmse_cv')}, Test RMSE: {p.get('rmse_test')}")
    else:
        lines.append(f"  CV MCC: {p.get('r2_cv')}, Test MCC: {p.get('r2_test')}")
    
    lines.append("")
    
    # Dataset size
    n_train = p.get("n_train")
    n_descriptors = p.get("n_descriptors")
    lines.append(f"Dataset: {n_train} training samples, {n_descriptors} descriptors")
    
    if p.get("points_descp_ratio"):
        lines.append(f"  Ratio: {p.get('points_descp_ratio')}")
    lines.append("")
    
    # Verification
    verify_passed = v.get("passed_tests", 0)
    verify_failed = v.get("failed_tests", 0)
    verify_unclear = v.get("unclear_tests", 0)
    lines.append(
        f"Verification: {verify_passed} passed, {verify_failed} failed, {verify_unclear} unclear"
    )
    
    if v.get("flawed_mod_score"):
        lines.append(f"  Flawed model score: {v.get('flawed_mod_score')}")
    lines.append("")
    
    # Key warnings from interpretation layer
    observations = diagnosis_json.get("observations", {}).get(best_variant, [])
    warnings = [ob for ob in observations if ob.get("level", "").lower() in ("warning", "failed")]
    
    if warnings:
        lines.append("Key findings:")
        for i, ob in enumerate(warnings[:3], 1):
            lines.append(f"  {i}. {ob.get('message', '')}")
        lines.append("")
    
    evidence_text = "\n".join(lines)
    budget.add_context(evidence_text)
    
    logger.debug(f"Evidence packed: {len(evidence_text)} chars, {budget.context_tokens} est. tokens")
    
    return evidence_text, budget
