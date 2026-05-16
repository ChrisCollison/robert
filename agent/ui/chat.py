"""
Chat interface and LLM integration (Phase 2).

This module will handle:
- LLM API calls (OpenAI, etc.)
- Chat message formatting
- Context injection (diagnostic evidence)
- Error handling and timeouts

Currently: STUB - to be implemented in Phase 2
"""

import logging
from typing import Optional, Dict, Any

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
    # Phase 2 implementation
    raise NotImplementedError("Chat functionality coming in Phase 2")


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
    # Phase 2 implementation
    raise NotImplementedError("Chat functionality coming in Phase 2")


def format_chat_message(role: str, content: str) -> Dict[str, str]:
    """
    Format a single chat message (Phase 2).
    
    Args:
        role: "user" or "assistant"
        content: Message content
        
    Returns:
        Dict with keys: role, content
    """
    return {"role": role, "content": content}


# Placeholder for chat state (Phase 2)
CHAT_HISTORY = []
