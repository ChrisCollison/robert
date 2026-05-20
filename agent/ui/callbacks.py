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
import json
from pathlib import Path
from datetime import datetime
from typing import Tuple, List, Dict, Any, Optional
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


def _contextualize_plot_followup(user_message: str, history: List[Dict[str, Any]]) -> str:
    """Expand ambiguous plot follow-ups with the prior user turn for routing."""
    text = (user_message or "").strip()
    if not text:
        return text

    q = text.lower()
    is_ambiguous_plot_followup = any(
        term in q
        for term in (
            "specific plot",
            "that plot",
            "this plot",
            "surface the plot",
            "surface that",
            "surface this",
            "show that plot",
            "show this plot",
        )
    )
    if not is_ambiguous_plot_followup:
        return text

    history_items = history if isinstance(history, list) else []
    for msg in reversed(history_items):
        if not isinstance(msg, dict):
            continue
        if msg.get("role") != "user":
            continue
        prev = str(msg.get("content", "")).strip()
        if prev:
            return f"{prev} {text}"

    return text


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


def _render_artifact_cards(run_context: Dict[str, Any], artifacts: List[Dict[str, Any]]) -> List[Any]:
    """Render image attachments for assistant chat messages."""
    if not isinstance(run_context, dict) or not isinstance(artifacts, list) or not artifacts:
        return []

    run_root_value = run_context.get("results_dir")
    if not isinstance(run_root_value, str) or not run_root_value:
        return []

    run_root = Path(run_root_value)
    if not run_root.exists():
        return []

    image_lookup = {image["path"]: image for image in find_evidence_images(str(run_root), run_context)}
    cards: List[Any] = []

    for artifact in artifacts:
        if not isinstance(artifact, dict):
            continue
        artifact_path = artifact.get("path")
        if not isinstance(artifact_path, str) or not artifact_path:
            continue

        if Path(artifact_path).is_absolute():
            resolved_path = str(Path(artifact_path).resolve())
        else:
            # Artifact paths in run_context are relative to the run outputs folder.
            resolved_path = str((run_root / "outputs" / artifact_path).resolve())
        image = image_lookup.get(resolved_path)
        if not image:
            continue

        title = artifact.get("label") or image["name"]
        variant = str(artifact.get("variant", "")).upper()
        subtitle = f"{variant} • {image['name']}" if variant else image["name"]
        cards.append(
            dbc.Card(
                [
                    dbc.CardHeader(title, className="small fw-semibold"),
                    dbc.CardBody(
                        [
                            html.Img(
                                src=image["data_uri"],
                                style={
                                    "width": "100%",
                                    "height": "auto",
                                    "maxHeight": "240px",
                                    "objectFit": "contain",
                                },
                            ),
                            html.Div(subtitle, className="small text-muted mt-2"),
                        ]
                    ),
                ],
                className="mt-2",
            )
        )

    return cards


def _render_chat_history(messages: List[Dict[str, str]], run_context: Dict[str, Any] = None) -> List[Any]:
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

        artifact_cards = _render_artifact_cards(run_context or {}, msg.get("artifacts", []))
        if artifact_cards:
            alert_children.append(html.Div(artifact_cards, className="mt-2"))

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
        State("response-style-store", "data"),
        State("chat-mode-store", "data"),
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
    response_style: str,
    chat_mode: str,
):
    """Handle user chat message with heuristics-first routing."""
    _ = (send_clicks, n_submit)
    if not user_message or not user_message.strip():
        return no_update, no_update, ""

    if not isinstance(run_context, dict):
        content = "Select a run first so the assistant can use run-specific evidence."
        base_history = history if isinstance(history, list) else []
        updated = base_history + [format_chat_message("assistant", content, source="assistant")]
        return updated, _render_chat_history(updated, run_context), ""

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
        return updated_history, _render_chat_history(updated_history, run_context), ""

    routed_message = _contextualize_plot_followup(user_message, base_history)

    result = answer_question(
        routed_message,
        run_context,
        diagnosis_json,
        api_key,
        use_local_rag=local_rag_enabled,
        chat_mode=chat_mode or "HEURISTICS_FIRST",
        response_style=response_style or "REPORT_ONLY",
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
            artifacts=result.get("artifacts", []),
        )
    )

    return updated_history, _render_chat_history(updated_history, run_context), ""


@callback(
    Output("response-style-store", "data"),
    Input("response-style-selector", "value"),
    prevent_initial_call=False,
)
def sync_response_style(selected_style: str) -> str:
    """Sync response style selector to store."""
    return selected_style or "REPORT_ONLY"


@callback(
    Output("chat-mode-store", "data"),
    Input("chat-mode-selector", "value"),
    prevent_initial_call=False,
)
def sync_chat_mode(selected_mode: str) -> str:
    """Sync chat mode selector to store."""
    return selected_mode or "HEURISTICS_FIRST"


def _slugify_filename_fragment(value: str, fallback: str = "run") -> str:
    """Convert free text to a conservative filename fragment."""
    text = (value or "").strip()
    if not text:
        return fallback
    cleaned = []
    for ch in text:
        if ch.isalnum() or ch in {"-", "_"}:
            cleaned.append(ch)
        elif ch in {" ", ".", "/", "\\"}:
            cleaned.append("-")
    result = "".join(cleaned).strip("-")
    return result or fallback


def _build_chat_export_payload(
    history: List[Dict[str, Any]],
    run_context: Dict[str, Any],
    response_style: str,
    chat_mode: str,
    local_rag_enabled: bool,
) -> Dict[str, Any]:
    """Build export payload for local transcript download."""
    run_name = "unknown-run"
    results_dir = ""
    if isinstance(run_context, dict):
        results_dir = str(run_context.get("results_dir", "") or "")
        run_name = str(run_context.get("run_name") or Path(results_dir).name or "unknown-run")

    messages = []
    for msg in history if isinstance(history, list) else []:
        if not isinstance(msg, dict):
            continue
        messages.append(
            {
                "role": msg.get("role", "assistant"),
                "content": msg.get("content", ""),
                "source": msg.get("source", "assistant"),
                "parity_status": msg.get("parity_status", ""),
                "tokens_input": msg.get("tokens_input", 0),
                "tokens_output": msg.get("tokens_output", 0),
                "cost_usd": msg.get("cost_usd", 0.0),
                "artifacts": msg.get("artifacts", []),
            }
        )

    return {
        "exported_at_utc": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "run_name": run_name,
        "results_dir": results_dir,
        "chat_mode": chat_mode or "HEURISTICS_FIRST",
        "response_style": response_style or "REPORT_ONLY",
        "local_rag_enabled": bool(local_rag_enabled),
        "message_count": len(messages),
        "messages": messages,
    }


def _extract_suggested_next_step(text: str) -> Optional[str]:
    """Extract 'Suggested next step' content from an assistant message when present."""
    if not text:
        return None
    lines = [line.strip() for line in str(text).splitlines()]
    for idx, line in enumerate(lines):
        lowered = line.lower()
        if lowered.startswith("suggested next step"):
            candidate = line.split(":", 1)[1].strip() if ":" in line else ""
            if candidate:
                return candidate
            if idx + 1 < len(lines) and lines[idx + 1]:
                return lines[idx + 1]
    return None


def _build_deterministic_chemist_summary(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Build a reproducible local summary from chat messages without LLM."""
    questions: List[str] = []
    caveats: List[str] = []
    next_steps: List[str] = []

    caveat_markers = (
        "warning",
        "failed",
        "fail",
        "unavailable",
        "no api key",
        "parity",
        "limited",
        "missing",
    )

    for msg in messages if isinstance(messages, list) else []:
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role", "")).lower()
        content = str(msg.get("content", "")).strip()
        if not content:
            continue

        if role == "user":
            if content not in questions:
                questions.append(content)
            continue

        # Assistant-side deterministic extraction
        extracted = _extract_suggested_next_step(content)
        if extracted and extracted not in next_steps:
            next_steps.append(extracted)

        for line in [ln.strip() for ln in content.splitlines() if ln.strip()]:
            lowered = line.lower()
            if any(marker in lowered for marker in caveat_markers):
                if line not in caveats:
                    caveats.append(line)

    return {
        "mode": "deterministic",
        "question_count": len(questions),
        "key_questions": questions[:8],
        "key_caveats": caveats[:8],
        "suggested_next_steps": next_steps[:8],
    }


def _generate_llm_chemist_summary(
    payload: Dict[str, Any],
    api_key: str,
    model_name: str,
) -> Tuple[Optional[str], Optional[str]]:
    """Generate an optional chemist-friendly summary using LLM, returning (summary, error)."""
    try:
        from openai import OpenAI
    except ImportError:
        return None, "OpenAI package not installed in this environment."

    messages = payload.get("messages", [])
    compact_lines: List[str] = []
    for msg in messages[:30]:
        if not isinstance(msg, dict):
            continue
        role = str(msg.get("role", "assistant")).upper()
        content = str(msg.get("content", "")).strip().replace("\n", " ")
        if len(content) > 500:
            content = content[:500] + "..."
        compact_lines.append(f"{role}: {content}")

    deterministic = payload.get("summaries", {}).get("deterministic", {})
    system_prompt = (
        "You are preparing an export-only chemist summary for a ROBERT chat transcript. "
        "Use only the provided transcript content and deterministic notes. "
        "Do not invent metrics or claims. Be concise and plain-language."
    )
    user_prompt = (
        "Create a short chemist-facing summary with these headings:\n"
        "1) What was asked\n"
        "2) Main findings\n"
        "3) Caveats\n"
        "4) Suggested next step\n\n"
        f"Deterministic notes:\n{json.dumps(deterministic, ensure_ascii=True, indent=2)}\n\n"
        "Transcript excerpts:\n"
        + "\n".join(compact_lines)
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=350,
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:
            return None, "LLM returned an empty summary."
        return text, None
    except Exception as exc:
        return None, f"LLM summary failed: {exc}"


def _to_markdown_transcript(payload: Dict[str, Any]) -> str:
    """Render export payload as a readable markdown transcript."""
    summaries = payload.get("summaries", {}) if isinstance(payload, dict) else {}
    deterministic = summaries.get("deterministic", {}) if isinstance(summaries, dict) else {}
    llm_summary = summaries.get("llm", {}) if isinstance(summaries, dict) else {}

    lines = [
        "# ROBERT Chat Export",
        "",
        f"- Exported (UTC): {payload.get('exported_at_utc', '')}",
        f"- Run: {payload.get('run_name', '')}",
        f"- Results dir: {payload.get('results_dir', '')}",
        f"- Chat mode: {payload.get('chat_mode', '')}",
        f"- Response style: {payload.get('response_style', '')}",
        f"- Local RAG enabled: {payload.get('local_rag_enabled', False)}",
        f"- Message count: {payload.get('message_count', 0)}",
        "",
        "## Chemist Summary (Deterministic)",
        "",
        f"- Questions captured: {deterministic.get('question_count', 0)}",
    ]

    for question in deterministic.get("key_questions", []):
        lines.append(f"- Question: {question}")
    for caveat in deterministic.get("key_caveats", []):
        lines.append(f"- Caveat: {caveat}")
    for step in deterministic.get("suggested_next_steps", []):
        lines.append(f"- Suggested next step: {step}")

    lines.extend([
        "",
        "## Chemist Summary (LLM Optional)",
        "",
        f"- Enabled: {llm_summary.get('enabled', False)}",
        f"- Generated: {llm_summary.get('generated', False)}",
        f"- Model: {llm_summary.get('model', '')}",
    ])

    if llm_summary.get("error"):
        lines.append(f"- Error: {llm_summary.get('error')}")
    if llm_summary.get("content"):
        lines.append("")
        lines.append(str(llm_summary.get("content", "")).strip())

    lines.extend([
        "",
        "## Transcript",
        "",
    ])

    for idx, msg in enumerate(payload.get("messages", []), start=1):
        role = str(msg.get("role", "assistant")).upper()
        source = msg.get("source", "assistant")
        parity = msg.get("parity_status", "")
        lines.append(f"### {idx}. {role}")
        lines.append(f"- Source: {source}")
        if parity:
            lines.append(f"- Parity: {parity}")
        tokens_in = msg.get("tokens_input", 0)
        tokens_out = msg.get("tokens_output", 0)
        cost = msg.get("cost_usd", 0.0)
        if tokens_in or tokens_out or cost:
            lines.append(f"- Tokens in/out: {tokens_in}/{tokens_out}")
            lines.append(f"- Estimated cost: ${float(cost):.4f}")
        lines.append("")
        lines.append(str(msg.get("content", "")).strip())
        lines.append("")

    return "\n".join(lines).strip() + "\n"


@callback(
    [
        Output("chat-export-download", "data"),
        Output("chat-export-status", "children"),
    ],
    Input("export-chat-button", "n_clicks"),
    [
        State("chat-export-format", "value"),
        State("chat-export-llm-summary", "value"),
        State("chat-history-store", "data"),
        State("run-context-store", "data"),
        State("response-style-store", "data"),
        State("chat-mode-store", "data"),
        State("local-rag-enabled-store", "data"),
    ],
    prevent_initial_call=True,
)
def export_chat_history(
    n_clicks: int,
    export_format: str,
    llm_summary_toggle: List[str],
    history: List[Dict[str, Any]],
    run_context: Dict[str, Any],
    response_style: str,
    chat_mode: str,
    local_rag_enabled: bool,
):
    """Download local chat transcript as JSON or Markdown."""
    _ = n_clicks
    if not isinstance(history, list) or not history:
        return no_update, "No chat history to export yet."

    payload = _build_chat_export_payload(
        history=history,
        run_context=run_context if isinstance(run_context, dict) else {},
        response_style=response_style or "REPORT_ONLY",
        chat_mode=chat_mode or "HEURISTICS_FIRST",
        local_rag_enabled=bool(local_rag_enabled),
    )

    deterministic_summary = _build_deterministic_chemist_summary(payload.get("messages", []))
    payload["summaries"] = {
        "deterministic": deterministic_summary,
        "llm": {
            "enabled": False,
            "generated": False,
            "model": "",
            "error": "",
            "content": "",
        },
    }

    status_note = "Export includes deterministic chemist summary."
    llm_enabled = isinstance(llm_summary_toggle, list) and ("enabled" in llm_summary_toggle)
    if llm_enabled:
        config = get_config()
        api_key = config.get("api_key")
        model_name = str(config.get("openai_model") or "gpt-4o-mini")
        payload["summaries"]["llm"]["enabled"] = True
        payload["summaries"]["llm"]["model"] = model_name

        if not api_key:
            payload["summaries"]["llm"]["error"] = "ROBERT_CHAT_API_KEY is not configured."
            status_note = "Deterministic summary exported; optional LLM summary skipped (no API key)."
        else:
            summary_text, llm_error = _generate_llm_chemist_summary(payload, api_key, model_name)
            if llm_error:
                payload["summaries"]["llm"]["error"] = llm_error
                status_note = "Deterministic summary exported; optional LLM summary failed."
            else:
                payload["summaries"]["llm"]["generated"] = True
                payload["summaries"]["llm"]["content"] = summary_text or ""
                status_note = "Export includes deterministic + optional LLM chemist summaries."

    run_fragment = _slugify_filename_fragment(str(payload.get("run_name", "run")), fallback="run")
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    if (export_format or "json").lower() == "md":
        markdown_text = _to_markdown_transcript(payload)
        filename = f"robert_chat_{run_fragment}_{ts}.md"
        return dcc.send_string(markdown_text, filename), f"Exported {payload.get('message_count', 0)} messages as Markdown. {status_note}"

    json_text = json.dumps(payload, indent=2, ensure_ascii=True)
    filename = f"robert_chat_{run_fragment}_{ts}.json"
    return dcc.send_string(json_text, filename), f"Exported {payload.get('message_count', 0)} messages as JSON. {status_note}"
