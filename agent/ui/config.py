"""
Configuration management for ROBERT UI.

Handles:
- API key loading from environment variables and config files
- Path resolution
- Default settings
"""

import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def resolve_ui_root() -> Path:
    """
    Find the UI root directory (agent/ui/).
    
    Returns:
        Path to agent/ui/ directory
        
    Raises:
        FileNotFoundError: If UI root cannot be found
    """
    ui_path = Path(__file__).parent
    if ui_path.name == "ui" and (ui_path.parent / "run_archive").exists():
        return ui_path.resolve()
    
    raise FileNotFoundError(
        f"Could not locate agent/ui/ directory. Current path: {ui_path}"
    )


def resolve_project_root() -> Path:
    """
    Find the project root (where AGENTS.md and robert/ are located).
    
    Returns:
        Path to project root
        
    Raises:
        FileNotFoundError: If project root cannot be found
    """
    candidates = [
        Path(__file__).parent.parent.parent,
        Path.cwd(),
        Path.cwd().parent,
        Path.cwd().parent.parent,
    ]
    
    for candidate in candidates:
        if (candidate / "AGENTS.md").exists() and (candidate / "robert").exists():
            return candidate.resolve()
    
    raise FileNotFoundError(
        f"Could not locate project root (AGENTS.md + robert/). Candidates: {candidates}"
    )


def load_api_key() -> Optional[str]:
    """
    Load API key from environment variable or config file.
    
    Priority:
    1. ROBERT_CHAT_API_KEY environment variable
    2. config/.env file (local override)
    
    Returns:
        API key string, or None if not found
        
    Note:
        - Key is loaded at startup and stored server-side
        - Never exposed to browser
        - If not found, app logs warning but continues
    """
    # Check environment variable
    key = os.getenv("ROBERT_CHAT_API_KEY")
    if key and key.strip():
        logger.info("API key loaded from ROBERT_CHAT_API_KEY environment variable")
        return key.strip()
    
    # Check local config file
    try:
        ui_root = resolve_ui_root()
        config_file = ui_root / "config" / ".env"
        if config_file.exists():
            with open(config_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("ROBERT_CHAT_API_KEY="):
                        key = line.split("=", 1)[1].strip()
                        if key:
                            logger.info(f"API key loaded from {config_file}")
                            return key
    except Exception as e:
        logger.debug(f"Could not read config/.env: {e}")
    
    # Not found
    logger.warning(
        "ROBERT_CHAT_API_KEY not found. "
        "Set via environment variable or create config/.env. "
        "Chat functionality will not work."
    )
    return None


def get_run_archive_root() -> Path:
    """
    Get path to run archive directory.
    
    Returns:
        Path to agent/run_archive/
    """
    project_root = resolve_project_root()
    return (project_root / "agent" / "run_archive").resolve()


def get_config() -> dict:
    """
    Get full configuration dictionary.
    
    Returns:
        Dict with keys: api_key, ui_root, project_root, run_archive_root
    """
    ui_root = resolve_ui_root()
    project_root = resolve_project_root()
    run_archive_root = get_run_archive_root()
    api_key = load_api_key()
    
    return {
        "api_key": api_key,
        "ui_root": ui_root,
        "project_root": project_root,
        "run_archive_root": run_archive_root,
        "debug": os.getenv("ROBERT_UI_DEBUG", "").lower() == "true",
    }


# Default settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8050
DEFAULT_DEBUG = False
