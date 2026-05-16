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
                            html.Small(
                                id="api-key-status",
                                className="text-muted",
                                children="API key: Not configured",
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
            html.Div(
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
