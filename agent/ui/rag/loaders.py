"""Local document loaders for the experimental knowledge base."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


def compute_sha256(file_path: Path) -> str:
    """Return SHA256 for a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            hasher.update(block)
    return hasher.hexdigest()


def _extract_pdf_text(pdf_path: Path) -> str:
    """Extract text from a PDF using PyMuPDF (fitz)."""
    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF (fitz) is required for PDF support. "
            "Install UI dependencies with: pip install -r requirements_ui.txt"
        ) from exc

    text_blocks: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text_blocks.append(page_text)
    return "\n".join(text_blocks)


def extract_text(file_path: Path) -> str:
    """Extract text from a supported file type."""
    suffix = file_path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return _extract_pdf_text(file_path)
    raise ValueError(f"Unsupported extension: {suffix}")


def scan_knowledge_files(knowledge_dir: Path) -> list[Path]:
    """Recursively scan a knowledge directory for supported files."""
    if not knowledge_dir.exists():
        return []

    files = [
        path
        for path in knowledge_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files)


def load_documents(knowledge_dir: Path) -> list[dict[str, Any]]:
    """Load documents from disk and return extracted text records."""
    documents: list[dict[str, Any]] = []
    for path in scan_knowledge_files(knowledge_dir):
        text = extract_text(path)
        documents.append(
            {
                "source_path": str(path.resolve()),
                "source_name": path.name,
                "text": text,
                "file_sha256": compute_sha256(path),
            }
        )
    return documents
