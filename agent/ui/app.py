"""
ROBERT UI — Local browser interface for diagnostic visualization and chat.

This is a Dash application that runs locally on your machine.

To run:
    python app.py

Then open http://localhost:8050 in your browser.

API Key:
    Set ROBERT_CHAT_API_KEY environment variable or create config/.env

Governance:
    - Read-only access to ROBERT outputs
    - API key stored server-side only (never exposed to browser)
    - No modifications to ROBERT code
"""

import logging
from pathlib import Path
import dash
import dash_bootstrap_components as dbc
from dash import html

# Local imports
from config import get_config, DEFAULT_HOST, DEFAULT_PORT, DEFAULT_DEBUG
from utils import find_run_context_files
from components import create_main_layout, empty_layout
from callbacks import *  # noqa: F401,F403

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def initialize_app():
    """
    Initialize Dash application.
    
    Returns:
        Dash app instance
    """
    # Load configuration
    try:
        config = get_config()
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        config = {}
    
    api_key = config.get("api_key")
    run_archive_root = config.get("run_archive_root")
    
    logger.info(f"Project root: {config.get('project_root')}")
    logger.info(f"Run archive: {run_archive_root}")
    if api_key:
        logger.info(f"API key: {api_key[:10]}...")
    else:
        logger.warning(
            "API key not configured. Chat functionality will not work. "
            "Set ROBERT_CHAT_API_KEY environment variable or create config/.env"
        )
    
    # Create Dash app
    app = dash.Dash(
        __name__,
        external_stylesheets=[dbc.themes.BOOTSTRAP],
        suppress_callback_exceptions=True,
    )
    
    # Find available runs
    try:
        runs = find_run_context_files(run_archive_root)
        logger.info(f"Found {len(runs)} diagnostic runs")
        
        if runs:
            # Create dropdown options
            run_options = [
                {
                    "label": f"{run['dataset_name']} ({run['timestamp']})",
                    "value": run["path"],
                }
                for run in runs
            ]
            
            # Set main layout
            app.layout = dbc.Container(
                create_main_layout(run_options),
                fluid=True,
                className="py-4",
            )
        else:
            # No runs found
            logger.warning("No diagnostic runs found in archive")
            app.layout = empty_layout()
    
    except Exception as e:
        logger.error(f"Error discovering runs: {e}")
        app.layout = empty_layout()
    
    return app


def main():
    """
    Run the Dash application.
    """
    app = initialize_app()
    
    logger.info(f"Starting app on {DEFAULT_HOST}:{DEFAULT_PORT}")
    logger.info(f"Open http://{DEFAULT_HOST}:{DEFAULT_PORT} in your browser")
    logger.info("Press Ctrl+C to stop")
    
    app.run_server(
        host=DEFAULT_HOST,
        port=DEFAULT_PORT,
        debug=DEFAULT_DEBUG,
    )


if __name__ == "__main__":
    main()
