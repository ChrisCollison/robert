"""
Dash callbacks for ROBERT UI.

Handles:
- Run selection
- Document loading and display
- Chat interface (Phase 2)
"""

from dash import callback, Input, Output, State, dcc
import logging
from typing import Tuple
from .utils import (
    load_run_context,
    load_diagnosis_summary,
    load_diagnosis_json,
    format_metrics_table,
    markdown_to_html,
)
from .config import get_config

logger = logging.getLogger(__name__)


@callback(
    [
        Output("run-context-store", "data"),
        Output("diagnosis-store", "data"),
        Output("document-content", "children"),
    ],
    Input("run-selector", "value"),
    prevent_initial_call=False,
)
def update_document_on_run_selection(selected_run_path: str) -> Tuple:
    """
    Load and display diagnostic content when run is selected.
    
    Args:
        selected_run_path: Path to selected run's run_context.json
        
    Returns:
        Tuple of (run_context_json, diagnosis_json, document_content_html)
    """
    if not selected_run_path:
        return None, None, "No run selected."
    
    # Load run context
    run_context = load_run_context(selected_run_path)
    if not run_context:
        return None, None, "Error loading run context."
    
    # Get run directory for diagnosis files
    run_dir = "/".join(selected_run_path.split("/")[:-1])
    
    # Load diagnosis files
    diagnosis_summary = load_diagnosis_summary(run_dir)
    diagnosis_json = load_diagnosis_json(run_dir)
    
    # Build document content
    content = []
    
    # Add metrics table
    metrics_html = format_metrics_table(run_context)
    content.append(metrics_html)
    
    # Add diagnosis summary
    if diagnosis_summary:
        summary_html = markdown_to_html(diagnosis_summary)
        content.append(summary_html)
    else:
        content.append("<p class='text-muted'>No diagnostic summary available.</p>")
    
    # Convert to single HTML string
    document_content = "\n".join(
        [str(item) if hasattr(item, '__str__') else str(item) for item in content]
    )
    
    return run_context, diagnosis_json, document_content


@callback(
    Output("api-key-status", "children"),
    Input("run-selector", "value"),  # Trigger on page load
    prevent_initial_call=False,
)
def update_api_key_status(_) -> str:
    """
    Update API key status indicator.
    
    Returns:
        Status text for display
    """
    config = get_config()
    api_key = config.get("api_key")
    
    if api_key:
        # Show masked key
        masked = api_key[:10] + "..." if len(api_key) > 10 else "***"
        return f"API key: {masked}"
    else:
        return "API key: ⚠️ Not configured"


# Phase 2: Chat callbacks will be added here
# - handle_message(n_clicks, message, api_key, context)
# - update_chat_history(response)
