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


def _load_local_env_value(var_name: str) -> Optional[str]:
    """Load a variable from agent/ui/config/.env without exporting it globally."""
    try:
        ui_root = resolve_ui_root()
        config_file = ui_root / "config" / ".env"
        if not config_file.exists():
            return None

        with open(config_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == var_name:
                    resolved = value.strip()
                    if resolved:
                        return resolved
    except Exception as e:
        logger.debug(f"Could not read config/.env for {var_name}: {e}")

    return None


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
    local_key = _load_local_env_value("ROBERT_CHAT_API_KEY")
    if local_key:
        logger.info("API key loaded from agent/ui/config/.env")
        return local_key
    
    # Not found
    logger.warning(
        "ROBERT_CHAT_API_KEY not found. "
        "Set via environment variable or create config/.env. "
        "Chat functionality will not work."
    )
    return None


def load_openai_model(default: str = "gpt-4o-mini") -> str:
    """
    Load OpenAI model name from environment or local config/.env.

    Priority:
    1. ROBERT_OPENAI_MODEL environment variable
    2. config/.env value
    3. provided default
    """
    model = os.getenv("ROBERT_OPENAI_MODEL", "").strip()
    if model:
        return model

    local_model = _load_local_env_value("ROBERT_OPENAI_MODEL")
    if local_model:
        return local_model

    return default


def load_response_style(default: str = "REPORT_ONLY") -> str:
    """
    Load response instruction style from environment or local config/.env.

    Valid values: REPORT_ONLY, REPORT_WITH_KB
    Priority:
    1. ROBERT_RESPONSE_STYLE environment variable
    2. config/.env value
    3. provided default
    """
    style = os.getenv("ROBERT_RESPONSE_STYLE", "").strip().upper()
    if style in {"REPORT_ONLY", "REPORT_WITH_KB"}:
        return style

    local_style = _load_local_env_value("ROBERT_RESPONSE_STYLE")
    if local_style and local_style.upper() in {"REPORT_ONLY", "REPORT_WITH_KB"}:
        return local_style.upper()

    return default


def load_chat_mode(default: str = "HEURISTICS_FIRST") -> str:
    """
    Load chat routing mode from environment or local config/.env.

    Valid values: HEURISTICS_FIRST, LLM_ONLY
    Priority:
    1. ROBERT_CHAT_MODE environment variable
    2. config/.env value
    3. provided default
    """
    mode = os.getenv("ROBERT_CHAT_MODE", "").strip().upper()
    if mode in {"HEURISTICS_FIRST", "LLM_ONLY"}:
        return mode

    local_mode = _load_local_env_value("ROBERT_CHAT_MODE")
    if local_mode and local_mode.upper() in {"HEURISTICS_FIRST", "LLM_ONLY"}:
        return local_mode.upper()

    return default


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
        Dict with keys: api_key, ui_root, project_root, run_archive_root, openai_model, response_style, chat_mode
    """
    ui_root = resolve_ui_root()
    project_root = resolve_project_root()
    run_archive_root = get_run_archive_root()
    api_key = load_api_key()
    openai_model = load_openai_model()
    response_style = load_response_style()
    chat_mode = load_chat_mode()
    
    return {
        "api_key": api_key,
        "ui_root": ui_root,
        "project_root": project_root,
        "run_archive_root": run_archive_root,
        "openai_model": openai_model,
        "response_style": response_style,
        "chat_mode": chat_mode,
        "debug": os.getenv("ROBERT_UI_DEBUG", "").lower() == "true",
    }


# Default settings
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8050
DEFAULT_DEBUG = False
