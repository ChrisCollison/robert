"""
Utility functions for ROBERT UI.

Provides helpers for:
- Loading ROBERT diagnostic context
- Formatting markdown and HTML
- File I/O
- Path resolution
"""

import json
import base64
from mimetypes import guess_type
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
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
            run_context_path = run_dir / "run_context.json"
            if not run_context_path.exists():
                run_context_path = run_dir / "llm_run_bundle" / "run_context.json"
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
    path = Path(run_dir) / "diagnosis_summary.md"
    if not path.exists():
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
    path = Path(run_dir) / "diagnosis.json"
    if not path.exists():
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


def get_run_root_from_context_path(run_context_path: str) -> Path:
    """
    Resolve the run root from either run root or llm_run_bundle context paths.

    Args:
        run_context_path: Path to run_context.json

    Returns:
        Path to run root directory
    """
    path = Path(run_context_path).resolve()
    parent = path.parent
    if parent.name == "llm_run_bundle":
        return parent.parent
    return parent


def build_metrics_rows(
    run_context: Dict[str, Any],
    diagnosis_json: Optional[Dict[str, Any]] = None,
) -> List[Tuple[str, str]]:
    """
    Build a richer metrics list for UI display.

    Args:
        run_context: Parsed run_context.json
        diagnosis_json: Optional parsed diagnosis.json

    Returns:
        List of (label, value) tuples
    """
    predict = run_context.get("predict", {})
    no_pfi = predict.get("no_pfi", {}) if isinstance(predict, dict) else {}
    pfi = predict.get("pfi", {}) if isinstance(predict, dict) else {}

    verify = run_context.get("verify", {})
    verify_no_pfi = verify.get("no_pfi", {}) if isinstance(verify, dict) else {}
    verify_pfi = verify.get("pfi", {}) if isinstance(verify, dict) else {}

    score = run_context.get("score", {}) if isinstance(run_context.get("score"), dict) else {}
    parser_warnings = run_context.get("parser_warnings", [])

    rows: List[Tuple[str, str]] = [
        ("Prediction Type", str(run_context.get("pred_type", "unknown"))),
        ("Model", str(run_context.get("ml_model", "unknown"))),
        ("Dataset CSV", str(run_context.get("dataset_csv", "unknown"))),
        ("ROBERT Score (No PFI)", str(score.get("no_pfi", "N/A"))),
        ("ROBERT Score (PFI)", str(score.get("pfi", "N/A"))),
        ("No PFI: R2 CV/Test", f"{no_pfi.get('r2_cv', 'N/A')} / {no_pfi.get('r2_test', 'N/A')}"),
        ("No PFI: RMSE CV/Test", f"{no_pfi.get('rmse_cv', 'N/A')} / {no_pfi.get('rmse_test', 'N/A')}"),
        ("No PFI: MAE CV/Test", f"{no_pfi.get('mae_cv', 'N/A')} / {no_pfi.get('mae_test', 'N/A')}"),
        ("No PFI: Train/Test Points", f"{no_pfi.get('n_train', 'N/A')} / {no_pfi.get('n_test', 'N/A')}"),
        ("No PFI: Descriptors", f"{no_pfi.get('n_descriptors', 'N/A')} ({', '.join(no_pfi.get('descriptors', []) or [])})"),
        ("PFI: R2 CV/Test", f"{pfi.get('r2_cv', 'N/A')} / {pfi.get('r2_test', 'N/A')}"),
        ("PFI: RMSE CV/Test", f"{pfi.get('rmse_cv', 'N/A')} / {pfi.get('rmse_test', 'N/A')}"),
        ("PFI: MAE CV/Test", f"{pfi.get('mae_cv', 'N/A')} / {pfi.get('mae_test', 'N/A')}"),
        ("PFI: Train/Test Points", f"{pfi.get('n_train', 'N/A')} / {pfi.get('n_test', 'N/A')}"),
        ("PFI: Descriptors", f"{pfi.get('n_descriptors', 'N/A')} ({', '.join(pfi.get('descriptors', []) or [])})"),
        (
            "VERIFY (No PFI)",
            f"passed={verify_no_pfi.get('passed_tests', 'N/A')}, "
            f"unclear={verify_no_pfi.get('unclear_tests', 'N/A')}, "
            f"failed={verify_no_pfi.get('failed_tests', 'N/A')}",
        ),
        (
            "VERIFY (PFI)",
            f"passed={verify_pfi.get('passed_tests', 'N/A')}, "
            f"unclear={verify_pfi.get('unclear_tests', 'N/A')}, "
            f"failed={verify_pfi.get('failed_tests', 'N/A')}",
        ),
        ("Parser Warnings", str(len(parser_warnings) if isinstance(parser_warnings, list) else 0)),
    ]

    if diagnosis_json:
        rows.append(("Diagnosis Timestamp", str(diagnosis_json.get("diagnosed_at", "N/A"))))

    return rows


def _candidate_image_paths(run_dir: Path, run_context: Dict[str, Any]) -> List[Path]:
    """
    Collect likely image artifact paths from parsed run_context.

    Args:
        run_dir: Run root directory
        run_context: Parsed run_context.json

    Returns:
        List of unique existing image paths
    """
    candidates: List[Path] = []
    outputs_dir = run_dir / "outputs"

    def add_artifact_paths(section: Dict[str, Any]) -> None:
        artifacts = section.get("artifacts", {}) if isinstance(section, dict) else {}
        for value in artifacts.values():
            if isinstance(value, str):
                p = outputs_dir / value
                candidates.append(p)

    predict = run_context.get("predict", {})
    if isinstance(predict, dict):
        add_artifact_paths(predict.get("no_pfi", {}))
        add_artifact_paths(predict.get("pfi", {}))

    # Fallback: include report assets if they contain image files.
    report_assets = run_dir / "report_assets"
    if report_assets.exists():
        candidates.extend(report_assets.glob("*.png"))
        candidates.extend(report_assets.glob("*.jpg"))
        candidates.extend(report_assets.glob("*.jpeg"))

    unique_existing: List[Path] = []
    seen = set()
    for path in candidates:
        if path.exists() and path.is_file() and path.suffix.lower() in {".png", ".jpg", ".jpeg"}:
            key = str(path.resolve())
            if key not in seen:
                seen.add(key)
                unique_existing.append(path.resolve())

    return unique_existing


def _image_to_data_uri(image_path: Path) -> Optional[str]:
    """
    Convert an image file to a base64 data URI for Dash display.

    Args:
        image_path: Path to image file

    Returns:
        Data URI string or None if conversion fails
    """
    try:
        mime_type, _ = guess_type(str(image_path))
        if not mime_type:
            mime_type = "image/png"
        encoded = base64.b64encode(image_path.read_bytes()).decode("ascii")
        return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        logger.warning(f"Could not encode image {image_path}: {e}")
        return None


def find_evidence_images(run_dir: str, run_context: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Return image evidence metadata for UI rendering.

    Args:
        run_dir: Run root directory
        run_context: Parsed run_context.json

    Returns:
        List of dicts with keys: name, path, data_uri
    """
    root = Path(run_dir)
    images = []
    for path in _candidate_image_paths(root, run_context):
        data_uri = _image_to_data_uri(path)
        if data_uri:
            images.append(
                {
                    "name": path.name,
                    "path": str(path),
                    "data_uri": data_uri,
                }
            )
    return images


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
