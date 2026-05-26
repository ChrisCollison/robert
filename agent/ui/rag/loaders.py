"""Local document loaders for the experimental knowledge base.
This file does 4 things:
1. Decide which file types are allowed.
2. Find those files inside the knowledge folder.
3. Extract text from each file.
4. Record metadata so each chunk can later be traced back to its source.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

# Only these file types will be included in the local knowledge base.
# Other files in the folder are ignored.
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


# Read the file and produce a unique ID based on its exact contents.
# If the file changes, this fingerprint changes too.
# This is useful because the system can later tell whether a file changed.
# Even if the filename stays the same, the SHA256 value changes when the file contents change.
# The code reads the file in blocks so it does not load a large PDF into memory all at once.
def compute_sha256(file_path: Path) -> str:
    """Return SHA256 for a file."""
    hasher = hashlib.sha256()
    with file_path.open("rb") as handle:
        # Stream in fixed-size blocks to avoid loading large PDFs fully into memory.
        for block in iter(lambda: handle.read(65536), b""):
            hasher.update(block)
    return hasher.hexdigest()

# Open the PDF, read each page, pull out the text, and combine all pages into one text string.
# Extract selectable text from a PDF.
# This does not OCR scanned images or figure text.
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


# Read text from a supported knowledge-base file.
# Markdown and text files are read directly.
# PDFs are opened page by page and converted to text.
def extract_text(file_path: Path) -> str:
    """Extract text from a supported file type."""
    suffix = file_path.suffix.lower()
    if suffix in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    if suffix == ".pdf":
        return _extract_pdf_text(file_path)
    raise ValueError(f"Unsupported extension: {suffix}")


# Find all supported knowledge files inside the folder and its subfolders.
# Sort them so the index is built in the same order each time.
def scan_knowledge_files(knowledge_dir: Path) -> list[Path]:
    """Recursively scan a knowledge directory for supported files."""
    if not knowledge_dir.exists():
        return []

    # Keep discovery deterministic so repeated builds produce stable ordering.
    files = [
        path
        for path in knowledge_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]
    return sorted(files)

# Load every supported file in the knowledge folder.
# For each file, keep the extracted text and source metadata.
# This metadata lets later chunks be traced back to the original file.
def load_documents(knowledge_dir: Path) -> list[dict[str, Any]]:
    """Load documents from disk and return extracted text records."""
    documents: list[dict[str, Any]] = []
    for path in scan_knowledge_files(knowledge_dir):
        text = extract_text(path)
        documents.append(
            {
                # Store enough metadata to trace every chunk back to its source file.
                "source_path": str(path.resolve()),
                "source_name": path.name,
                "text": text,
                "file_sha256": compute_sha256(path),
            }
        )
    return documents
