"""
Utility functions for ROBERT UI.

Provides helpers for:
- Loading ROBERT diagnostic context
- Formatting markdown and HTML
- File I/O
- Path resolution
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def find_run_context_files(run_archive_root: Path) -> list[Dict[str, Any]]:
    """
    Find all run_context.json files in the run archive.
    
    Args:
        run_archive_root: Path to agent/run_archive/
        
    Returns:
        List of dicts with keys: path, timestamp, dataset_name
        Sorted by timestamp (newest first)
    """
    if not run_archive_root.exists():
        logger.warning(f"Run archive not found: {run_archive_root}")
        return []
    
    runs = []
    for run_dir in run_archive_root.iterdir():
        if run_dir.is_dir():
            run_context_path = run_dir / "outputs" / "run_context.json"
            if run_context_path.exists():
                # Extract dataset name from folder name (format: TIMESTAMP__DATASETNAME)
                folder_name = run_dir.name
                try:
                    dataset_name = folder_name.split("__", 1)[1] if "__" in folder_name else folder_name
                except:
                    dataset_name = folder_name
                
                runs.append({
                    "path": str(run_context_path),
                    "folder": str(run_dir),
                    "timestamp": folder_name.split("__")[0] if "__" in folder_name else folder_name,
                    "dataset_name": dataset_name,
                })
    
    # Sort by timestamp (newest first)
    runs.sort(key=lambda x: x["timestamp"], reverse=True)
    return runs


def load_run_context(run_context_path: str) -> Optional[Dict[str, Any]]:
    """
    Load run_context.json from disk.
    
    Args:
        run_context_path: Path to run_context.json file
        
    Returns:
        Parsed JSON dict, or None if file not found
    """
    path = Path(run_context_path)
    if not path.exists():
        logger.error(f"run_context.json not found: {run_context_path}")
        return None
    
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading {run_context_path}: {e}")
        return None


def load_diagnosis_summary(run_dir: str) -> Optional[str]:
    """
    Load diagnosis_summary.md from run folder.
    
    Args:
        run_dir: Path to run folder (e.g., agent/run_archive/20260514_120000__Hvapor/)
        
    Returns:
        Markdown content as string, or None if file not found
    """
    path = Path(run_dir) / "outputs" / "diagnosis_summary.md"
    if not path.exists():
        logger.debug(f"diagnosis_summary.md not found: {path}")
        return None
    
    try:
        with open(path, "r") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error loading diagnosis_summary.md: {e}")
        return None


def load_diagnosis_json(run_dir: str) -> Optional[Dict[str, Any]]:
    """
    Load diagnosis.json from run folder.
    
    Args:
        run_dir: Path to run folder
        
    Returns:
        Parsed JSON dict, or None if file not found
    """
    path = Path(run_dir) / "outputs" / "diagnosis.json"
    if not path.exists():
        logger.debug(f"diagnosis.json not found: {path}")
        return None
    
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading diagnosis.json: {e}")
        return None


def format_metrics_table(run_context: Dict[str, Any]) -> str:
    """
    Format run_context metrics as an HTML table.
    
    Args:
        run_context: Parsed run_context.json
        
    Returns:
        HTML string for metrics table
    """
    rows = []
    
    # Extract key metrics
    metrics = {
        "Prediction Type": run_context.get("pred_type", "unknown"),
        "ML Model": run_context.get("ml_model", "unknown"),
        "Dataset": run_context.get("results_dir", "unknown").split("/")[-1] if run_context.get("results_dir") else "unknown",
    }
    
    # Add prediction metrics
    if run_context.get("available", {}).get("predict"):
        metrics["CV R² (No PFI)"] = f"{run_context.get('predict', {}).get('no_pfi', {}).get('r2_cv', 'N/A')}"
        metrics["Test R² (No PFI)"] = f"{run_context.get('predict', {}).get('no_pfi', {}).get('r2_test', 'N/A')}"
    
    html = "<table class='metrics-table' style='width: 100%; border-collapse: collapse;'>\n"
    for key, value in metrics.items():
        html += f"  <tr style='border-bottom: 1px solid #ddd;'>\n"
        html += f"    <td style='padding: 8px; font-weight: bold;'>{key}</td>\n"
        html += f"    <td style='padding: 8px;'>{value}</td>\n"
        html += f"  </tr>\n"
    html += "</table>\n"
    
    return html


def markdown_to_html(markdown_text: str) -> str:
    """
    Convert markdown to HTML using simple pattern matching.
    
    Note: For production, consider using a library like markdown2 or pypandoc.
    
    Args:
        markdown_text: Markdown string
        
    Returns:
        HTML string
    """
    if not markdown_text:
        return "<p>No content available.</p>"
    
    try:
        import markdown
        return markdown.markdown(markdown_text)
    except ImportError:
        # Fallback: simple HTML escaping
        import html
        return f"<pre>{html.escape(markdown_text)}</pre>"


def get_latest_run(run_archive_root: Path) -> Optional[Dict[str, Any]]:
    """
    Get the most recent run from the archive.
    
    Args:
        run_archive_root: Path to agent/run_archive/
        
    Returns:
        Dict with run metadata, or None if no runs found
    """
    runs = find_run_context_files(run_archive_root)
    return runs[0] if runs else None
