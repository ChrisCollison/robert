"""
Dash callbacks for ROBERT UI.

Handles:
- Run selection
- Document loading and display
- Chat interface (Phase 2)
"""

from dash import callback, Input, Output, State, html, dcc, no_update
import dash_bootstrap_components as dbc
import logging
from typing import Tuple, List, Dict, Any
from utils import (
    load_run_context,
    load_diagnosis_summary,
    load_diagnosis_json,
    build_metrics_rows,
    find_evidence_images,
    get_run_root_from_context_path,
)
from config import get_config
from chat import answer_question, format_chat_message
from parity import check_parity

logger = logging.getLogger(__name__)


def _severity_badge(level: str) -> dbc.Badge:
    """Map observation levels to consistent badge colors."""
    value = (level or "info").lower()
    color_map = {
        "passed": "success",
        "info": "secondary",
        "warning": "warning",
        "failed": "danger",
        "fail": "danger",
        "error": "danger",
    }
    color = color_map.get(value, "secondary")
    return dbc.Badge((level or "info").upper(), color=color, className="me-2")


def _render_observations(diagnosis_json: Dict[str, Any]) -> html.Div:
    observations = diagnosis_json.get("observations", {}) if isinstance(diagnosis_json, dict) else {}
    if not isinstance(observations, dict):
        return html.Div(html.P("No structured observations available.", className="text-muted"))

    sections = []
    for section_name in ["no_pfi", "pfi", "global"]:
        items = observations.get(section_name, [])
        if not items:
            continue

        rows = []
        for item in items:
            level = str(item.get("level", "info")) if isinstance(item, dict) else "info"
            message = str(item.get("message", "")) if isinstance(item, dict) else str(item)
            rows.append(
                html.Div(
                    [
                        _severity_badge(level),
                        html.Span(message, className="flex-grow-1"),
                    ],
                    className="mb-2 d-flex align-items-start gap-2",
                )
            )

        sections.append(
            html.Div(
                [
                    html.H6(section_name.upper(), className="mb-2 mt-3"),
                    html.Div(rows),
                ]
            )
        )

    if not sections:
        return html.Div(html.P("No structured observations available.", className="text-muted"))
    return html.Div(sections)


def _render_chat_history(messages: List[Dict[str, str]]) -> List[Any]:
    if not messages:
        return [html.P("Ask a question about why this run got its score.", className="text-muted")]

    blocks: List[Any] = []
    for msg in messages:
        role = msg.get("role", "assistant")
        content = msg.get("content", "")
        source = msg.get("source", "assistant")
        parity_status = msg.get("parity_status", "")
        tokens_in = msg.get("tokens_input", 0)
        tokens_out = msg.get("tokens_output", 0)
        cost_usd = msg.get("cost_usd", 0.0)

        if role == "user":
            blocks.append(
                dbc.Alert(content, color="light", className="mb-2", style={"border": "1px solid #dcdcdc"})
            )
            continue

        badge_text = {
            "heuristic": "Heuristic",
            "local-rag": "Local RAG",
            "openai": "OpenAI",
            "fallback-disabled": "Fallback Disabled",
            "no-api-key": "No API Key",
            "parity-fail": "Parity Block",
        }.get(source, "Assistant")

        parity_map = {
            "pass": ("Verified", "success"),
            "incomplete": ("Partial", "warning"),
            "fail": ("Unverified", "danger"),
        }
        parity_badge = None
        if parity_status in parity_map:
            text, color = parity_map[parity_status]
            parity_badge = dbc.Badge(text, color=color, className="me-2")

        # Token/cost footer (only show if tokens were used)
        token_footer = None
        if tokens_in > 0 or cost_usd > 0:
            token_footer = html.Div(
                f"Tokens: {tokens_in} in, {tokens_out} out | Est. cost: ${cost_usd:.4f}",
                className="small text-muted mt-2",
            )

        alert_children = [
            dbc.Badge(badge_text, color="info", className="me-2"),
            parity_badge,
            html.Span(content),
        ]
        if token_footer:
            alert_children.append(token_footer)

        blocks.append(
            dbc.Alert(
                alert_children,
                color="primary",
                className="mb-2",
            )
        )
    return blocks


@callback(
    [
        Output("run-context-store", "data"),
        Output("diagnosis-store", "data"),
        Output("parity-store", "data"),
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
        return None, None, None, "No run selected."
    
    # Load run context
    run_context = load_run_context(selected_run_path)
    if not run_context:
        return None, None, None, "Error loading run context."
    
    # Resolve run root even when selected path is in llm_run_bundle
    run_dir = str(get_run_root_from_context_path(selected_run_path))

    parity_result = check_parity(run_context, get_run_root_from_context_path(selected_run_path))
    
    # Load diagnosis files
    diagnosis_summary = load_diagnosis_summary(run_dir)
    diagnosis_json = load_diagnosis_json(run_dir)
    
    metrics_rows = build_metrics_rows(run_context, diagnosis_json)
    metrics_table = dbc.Table(
        [
            html.Thead(html.Tr([html.Th("Metric"), html.Th("Value")])),
            html.Tbody([
                html.Tr([html.Td(label, className="fw-semibold"), html.Td(value)])
                for label, value in metrics_rows
            ]),
        ],
        bordered=True,
        hover=True,
        responsive=True,
        striped=True,
        size="sm",
        className="mb-4",
    )

    if diagnosis_summary:
        summary_component = dcc.Markdown(
            diagnosis_summary,
            link_target="_blank",
            style={"whiteSpace": "pre-wrap", "lineHeight": "1.5"},
            className="mb-4",
        )
    else:
        summary_component = html.P("No diagnostic summary available.", className="text-muted")

    image_blocks = []
    for image in find_evidence_images(run_dir, run_context):
        image_blocks.append(
            dbc.Card(
                [
                    dbc.CardHeader(image["name"], className="small fw-semibold"),
                    dbc.CardBody(
                        [
                            html.Img(
                                src=image["data_uri"],
                                style={
                                    "width": "100%",
                                    "height": "auto",
                                    "maxHeight": "320px",
                                    "objectFit": "contain",
                                },
                            ),
                            html.Div(image["path"], className="small text-muted mt-2"),
                        ]
                    ),
                ],
                className="mb-3",
            )
        )

    if not image_blocks:
        image_blocks = [html.P("No image evidence found for this run.", className="text-muted")]

    observations_component = (
        _render_observations(diagnosis_json) if diagnosis_json else html.P("No observations available.", className="text-muted")
    )

    document_content = html.Div(
        [
            html.H6("Key Metrics", className="mb-2"),
            metrics_table,
            html.H6("Evidence-Linked Observations", className="mb-2"),
            observations_component,
            html.H6("Diagnosis Narrative", className="mb-2"),
            summary_component,
            html.H6("Evidence Images", className="mb-2"),
            html.Div(image_blocks),
        ]
    )
    
    return run_context, diagnosis_json, parity_result, document_content


@callback(
    [
        Output("chat-input", "disabled"),
        Output("send-button", "disabled"),
        Output("chat-guardrail-status", "children"),
        Output("chat-guardrail-status", "className"),
    ],
    Input("parity-store", "data"),
    prevent_initial_call=False,
)
def sync_chat_guardrail(parity_data: Dict[str, Any]) -> Tuple[bool, bool, str, str]:
    """Enable or disable chat based on parity verification result."""
    if not isinstance(parity_data, dict):
        return True, True, "Select a run to enable chat.", "text-muted"

    status = parity_data.get("parity_status")
    if status == "pass":
        return False, False, "Parity verified. Chat enabled.", "text-success"
    if status == "incomplete":
        return False, False, "Parity partial. Chat enabled with limited evidence.", "text-warning"

    return True, True, "Parity failed. Chat disabled until extraction is fixed.", "text-danger"


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


@callback(
    [
        Output("local-rag-enabled-store", "data"),
        Output("local-rag-toggle-status", "children"),
        Output("local-rag-toggle-status", "className"),
    ],
    Input("local-rag-toggle", "value"),
    prevent_initial_call=False,
)
def update_local_rag_toggle(toggle_values: List[str]) -> Tuple[bool, str, str]:
    """Persist session-level local RAG preference from UI toggle."""
    enabled = isinstance(toggle_values, list) and ("enabled" in toggle_values)
    if enabled:
        return True, "Local RAG: Enabled (session override)", "text-success"
    return False, "Local RAG: Disabled (session override)", "text-muted"


@callback(
    [
        Output("chat-history-store", "data"),
        Output("chat-messages", "children"),
        Output("chat-input", "value"),
    ],
    [
        Input("send-button", "n_clicks"),
        Input("chat-input", "n_submit"),
    ],
    [
        State("chat-input", "value"),
        State("chat-history-store", "data"),
        State("run-context-store", "data"),
        State("diagnosis-store", "data"),
        State("parity-store", "data"),
        State("local-rag-enabled-store", "data"),
    ],
    prevent_initial_call=True,
)
def handle_chat_message(
    send_clicks: int,
    n_submit: int,
    user_message: str,
    history: List[Dict[str, str]],
    run_context: Dict[str, Any],
    diagnosis_json: Dict[str, Any],
    parity_data: Dict[str, Any],
    local_rag_enabled: bool,
):
    """Handle user chat message with heuristics-first routing."""
    _ = (send_clicks, n_submit)
    if not user_message or not user_message.strip():
        return no_update, no_update, ""

    if not isinstance(run_context, dict):
        content = "Select a run first so the assistant can use run-specific evidence."
        base_history = history if isinstance(history, list) else []
        updated = base_history + [format_chat_message("assistant", content, source="assistant")]
        return updated, _render_chat_history(updated), ""

    config = get_config()
    api_key = config.get("api_key")

    base_history = history if isinstance(history, list) else []
    updated_history = base_history + [format_chat_message("user", user_message, source="user")]

    parity_status = "fail"
    if isinstance(parity_data, dict):
        parity_status = str(parity_data.get("parity_status", "fail"))

    if parity_status == "fail":
        blocked = (
            "Extraction verification failed for this run. "
            "Please contact the developer and provide the run ID for parity debugging."
        )
        updated_history.append(
            format_chat_message("assistant", blocked, source="parity-fail", parity_status=parity_status)
        )
        return updated_history, _render_chat_history(updated_history), ""

    result = answer_question(
        user_message,
        run_context,
        diagnosis_json,
        api_key,
        use_local_rag=local_rag_enabled,
    )
    reply = result.get("content", "No answer available.")
    if parity_status == "incomplete":
        reply = "Parity warning: this run has partial evidence coverage.\n\n" + reply

    updated_history.append(
        format_chat_message(
            "assistant",
            reply,
            source=result.get("source", "assistant"),
            parity_status=parity_status,
            tokens_input=result.get("tokens_input", 0),
            tokens_output=result.get("tokens_output", 0),
            cost_usd=result.get("cost_usd", 0.0),
        )
    )

    return updated_history, _render_chat_history(updated_history), ""
