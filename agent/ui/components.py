"""
Dash UI components for ROBERT interface.

Provides reusable layout components:
- Header with title and run selector
- Left panel (document viewer)
- Right panel (chat placeholder)
"""

import dash_bootstrap_components as dbc
from dash import dcc, html
from typing import List, Dict, Any
from guided_faq import get_starter_items, get_category_options


def create_header(run_options: List[Dict[str, str]]) -> dbc.Container:
    """
    Create header with title and run selector.
    
    Args:
        run_options: List of dicts with keys: label, value
        
    Returns:
        dbc.Container with header content
    """
    return dbc.Container(
        [
            dbc.Row(
                [
                    dbc.Col(
                        [
                            html.H1(
                                "ROBERT Score Explanation",
                                className="text-primary mb-0",
                            ),
                            html.P(
                                "Understand your ROBERT machine learning results",
                                className="text-muted mb-3",
                            ),
                            dbc.Button(
                                "ROBERT Report Summary",
                                id="report-summary-button",
                                color="primary",
                                size="md",
                                className="mb-2 mt-2",
                                n_clicks=0,
                            ),
                        ],
                        md=6,
                    ),
                    dbc.Col(
                        [
                            html.Label("Select a run:", className="fw-bold"),
                            dcc.Dropdown(
                                id="run-selector",
                                options=run_options,
                                value=run_options[0]["value"] if run_options else None,
                                clearable=False,
                                className="mb-2",
                            ),
                            dbc.Button(
                                "Refresh Runs",
                                id="refresh-runs-button",
                                color="secondary",
                                size="sm",
                                className="mb-2",
                                n_clicks=0,
                            ),
                            html.Br(),
                            html.Small(
                                id="run-refresh-status",
                                className="text-muted",
                                children="Run list loaded at startup.",
                            ),
                            html.Br(),
                            html.Small(
                                id="api-key-status",
                                className="text-muted",
                                children="API key: Not configured",
                            ),
                            html.Br(),
                            html.Div(
                                [
                                    dbc.Checklist(
                                        id="local-rag-toggle",
                                        options=[{"label": " Enable Local RAG retrieval", "value": "enabled"}],
                                        value=["enabled"],
                                        switch=True,
                                        className="mt-2",
                                    ),
                                    html.Small(
                                        id="local-rag-toggle-status",
                                        className="text-muted",
                                        children="Local RAG: Enabled (session)",
                                    ),
                                ]
                            ),
                            html.Hr(className="my-2"),
                            html.Label("Response Style:", className="fw-bold small"),
                            dcc.RadioItems(
                                id="response-style-selector",
                                options=[
                                    {"label": " Report Only (no KB)", "value": "REPORT_ONLY"},
                                    {"label": " Report with Knowledge Base", "value": "REPORT_WITH_KB"},
                                ],
                                value="REPORT_ONLY",
                                inline=False,
                                className="small",
                            ),
                            html.Label("Chat Mode:", className="fw-bold small mt-2"),
                            dcc.RadioItems(
                                id="chat-mode-selector",
                                options=[
                                    {"label": " Heuristics First", "value": "HEURISTICS_FIRST"},
                                    {"label": " LLM Only", "value": "LLM_ONLY"},
                                ],
                                value="HEURISTICS_FIRST",
                                inline=False,
                                className="small",
                            ),
                        ],
                        md=6,
                    ),
                ],
                className="align-items-center",
            ),
            html.Hr(className="my-3"),
        ],
        fluid=True,
        className="py-3",
    )


def create_document_panel() -> dbc.Col:
    """
    Create left-side document viewer panel.
    
    Returns:
        dbc.Col with document display area
    """
    return dbc.Col(
        [
            html.H5("Diagnostic Summary", className="mb-3"),
            html.P(
                "Use metrics and evidence images below to interpret what drove the score.",
                className="text-muted mb-3",
            ),
            html.Div(
                id="document-content",
                className="document-viewer",
                style={
                    "overflow-y": "auto",
                    "max-height": "82vh",
                    "padding": "20px",
                    "border": "1px solid #ddd",
                    "border-radius": "4px",
                    "background-color": "#ffffff",
                    "font-size": "0.97rem",
                    "line-height": "1.55",
                },
                children=html.P("Select a run to view diagnostics.", className="text-muted"),
            ),
        ],
        md=7,
        className="pe-2",
    )


def create_chat_panel() -> dbc.Col:
    """
    Create right-side chat panel.
    
    Returns:
        dbc.Col with chat interface placeholder
    """
    return dbc.Col(
        [
            html.H5("Chat Assistant", className="mb-3"),
            dcc.Loading(
                id="chat-loading",
                type="default",
                children=html.Div(
                    id="chat-messages",
                    className="chat-messages",
                    style={
                        "overflow-y": "auto",
                        "max-height": "70vh",
                        "padding": "15px",
                        "border": "1px solid #ddd",
                        "border-radius": "4px",
                        "background-color": "#f8f9fa",
                        "margin-bottom": "15px",
                    },
                    children=html.P(
                        "Ask a question about why this run got its score.",
                        className="text-muted",
                    ),
                ),
            ),
            html.Div(
                [
                    html.H6("Guided Starter Questions", className="mb-2"),
                    html.Small(
                        "These launch run-specific questions for the selected ROBERT result.",
                        className="text-muted d-block mb-2",
                    ),
                    dbc.Row(
                        [
                            dbc.Col(
                                dbc.Button(
                                    item["label"],
                                    id={"type": "guided-faq-starter", "faq_id": item["id"]},
                                    color="light",
                                    className="w-100 text-start",
                                    n_clicks=0,
                                ),
                                md=6,
                                className="mb-2",
                            )
                            for item in get_starter_items()
                        ],
                        className="g-2",
                    ),
                    dbc.Accordion(
                        [
                            dbc.AccordionItem(
                                [
                                    dcc.Dropdown(
                                        id={"type": "guided-faq-select", "category": group["id"]},
                                        options=group["options"],
                                        value=None,
                                        clearable=True,
                                        placeholder=f"Choose a question from {group['label']}",
                                        className="mb-2",
                                    ),
                                    dbc.Button(
                                        "Ask Selected Question",
                                        id={"type": "guided-faq-launch", "category": group["id"]},
                                        color="secondary",
                                        size="sm",
                                        n_clicks=0,
                                    ),
                                ],
                                title=group["label"],
                            )
                            for group in get_category_options(include_starters=False)
                        ],
                        start_collapsed=True,
                        className="mb-3",
                    ),
                    html.Small(
                        id="guided-faq-status",
                        children="",
                        className="text-muted d-block mb-2",
                    ),
                ],
                className="mb-3",
            ),
            dbc.InputGroup(
                [
                    dbc.Input(
                        id="chat-input",
                        placeholder="Ask a question about your results...",
                        type="text",
                        disabled=False,
                    ),
                    dbc.Button(
                        "Send",
                        id="send-button",
                        color="primary",
                        disabled=False,
                    ),
                ],
                className="mb-2",
            ),
            html.Small(
                "Heuristics-first answers are enabled. LLM fallback remains optional.",
                className="text-muted",
            ),
            html.Br(),
            html.Small(
                id="chat-guardrail-status",
                children="Select a run to enable chat.",
                className="text-muted",
            ),
            html.Hr(className="my-2"),
            html.Small(
                "Note: each answer uses your current question plus run evidence. "
                "Prior chat messages are not sent as context for this turn.",
                className="text-muted d-block mb-2",
            ),
            dbc.Row(
                [
                    dbc.Col(
                        dcc.Dropdown(
                            id="chat-export-format",
                            options=[
                                {"label": "JSON", "value": "json"},
                                {"label": "Markdown", "value": "md"},
                            ],
                            value="json",
                            clearable=False,
                        ),
                        md=6,
                    ),
                    dbc.Col(
                        dbc.Button(
                            "Export Chat",
                            id="export-chat-button",
                            color="secondary",
                            className="w-100",
                            n_clicks=0,
                        ),
                        md=6,
                    ),
                ],
                className="g-2 mt-1",
            ),
            dbc.Checklist(
                id="chat-export-llm-summary",
                options=[{"label": " Include optional LLM chemist summary in export", "value": "enabled"}],
                value=[],
                switch=True,
                className="mt-2",
            ),
            html.Small(
                id="chat-export-status",
                children="",
                className="text-muted d-block mt-2",
            ),
            dcc.Download(id="chat-export-download"),
        ],
        md=5,
        className="ps-2",
    )


def create_main_layout(run_options: List[Dict[str, str]]) -> html.Div:
    """
    Create main application layout.
    
    Args:
        run_options: List of available runs
        
    Returns:
        html.Div with full layout
    """
    return html.Div(
        [
            # Header
            create_header(run_options),

            # Summary output area (initially hidden/empty)
            dbc.Container(
                [
                    html.Div(
                        id="report-summary-output",
                        className="mb-4",
                        style={
                            "display": "none",  # Initially hidden until summary is generated
                            "backgroundColor": "#e9f7ef",
                            "border": "1px solid #b2dfdb",
                            "borderRadius": "6px",
                            "padding": "18px",
                            "fontSize": "1.05rem",
                        },
                        children="",
                    )
                ],
                fluid=True,
            ),
            
            # Main content (split screen)
            dbc.Container(
                [
                    dbc.Row(
                        [
                            create_document_panel(),
                            create_chat_panel(),
                        ],
                        className="g-3",
                    ),
                ],
                fluid=True,
                className="py-4",
            ),
            
            # Store for run context (Phase 2)
            dcc.Store(id="run-context-store"),
            dcc.Store(id="diagnosis-store"),
            dcc.Store(id="parity-store"),
            dcc.Store(id="chat-history-store", data=[]),
            dcc.Store(id="local-rag-enabled-store", data=None),
            dcc.Store(id="response-style-store", data="REPORT_ONLY"),
            dcc.Store(id="chat-mode-store", data="HEURISTICS_FIRST"),
        ],
        className="min-vh-100",
    )


def empty_layout() -> html.Div:
    """
    Create placeholder layout when no runs found.
    
    Returns:
        html.Div with instructions
    """
    return html.Div(
        [
            create_header([]),
            dbc.Container(
                [
                    dbc.Alert(
                        [
                            html.H4("No diagnostic runs found"),
                            html.P(
                                "To use this interface, you need to first run ROBERT and extract diagnostics."
                            ),
                            html.P(
                                [
                                    "Run the following notebooks in order:",
                                    html.Br(),
                                    html.Code("agent/robert_run_wrapper.ipynb"),
                                    " → ",
                                    html.Code("agent/extract_context.ipynb"),
                                    " → ",
                                    html.Code("agent/diagnose_score.ipynb"),
                                ]
                            ),
                            html.P(
                                "Then refresh this page.",
                                className="mb-0",
                            ),
                        ],
                        color="info",
                        className="mt-4",
                    )
                ],
                fluid=True,
            ),
        ],
    )
