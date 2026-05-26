"""Build a local BM25 knowledge index (Phase 1 experimental).
Build the local searchable knowledge base.
This is the indexing step that must happen before retrieval can work.

1. Find the knowledge folder.
2. Find the storage folder.
3. Load the documents from the knowledge folder.
4. Split those documents into smaller chunks.
5. Build a keyword-search index from the chunks.
6. Save three files:
   - chunks.jsonl
   - bm25.pkl
   - manifest.json
7. Return a short summary of what was built.
Your cleaned knowledge files
        ↓
build_index.py
        ↓
chunks.jsonl + bm25.pkl + manifest.json
        ↓
retrieve.py can now search them"""

from __future__ import annotations

import json
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# load_documents reads the files.
# chunk_document splits each loaded file into smaller searchable pieces.
from .chunking import chunk_document
from .loaders import SUPPORTED_EXTENSIONS, load_documents

# Find the main project folder from the location of this file.
def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]

# Convert a folder path into a full path.
# This lets the index builder work from notebooks, scripts, or the app.
def _resolve_path(path_like: Path | str) -> Path:
    path = Path(path_like)
    if path.is_absolute():
        return path

    # Prefer caller-relative paths first so notebook-local overrides work naturally.
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    # Fallback to project-root-relative paths for stable defaults.
    root_candidate = (_project_root() / path).resolve()
    return root_candidate

# Break text into simple lowercase search terms for BM25.
def _tokenize(text: str) -> list[str]:
    # Keep tokenization simple and deterministic for BM25 lexical retrieval.
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())

# Save all text chunks to a JSONL file.
# Each line is one chunk with its text and source metadata.
def _save_chunks_jsonl(chunks: list[dict[str, Any]], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=True) + "\n")

# Build the local knowledge index.
# Documents are loaded, split into chunks, indexed, and saved for later retrieval.
def build_local_index(
    knowledge_dir: Path | str = "agent/ui/knowledge",
    storage_dir: Path | str = "agent/ui/storage",
    chunk_size: int = 350,
    chunk_overlap: int = 75,
) -> dict[str, Any]:
    """Build a local BM25 index and persist artifacts to disk."""
    try:
        # BM25 is the keyword-search method used for local retrieval.
        from rank_bm25 import BM25Okapi  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "rank-bm25 is required. Install UI dependencies with: "
            "pip install -r requirements_ui.txt"
        ) from exc

    # Locate the knowledge folder and make sure the storage folder exists.
    knowledge_path = _resolve_path(knowledge_dir)
    storage_path = _resolve_path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)

    # Read all supported files from the knowledge folder.
    # Stop if the folder does not contain any usable files.
    documents = load_documents(knowledge_path)
    if not documents:
        raise ValueError(
            "No supported files found in knowledge folder. "
            "Add .txt, .md, or .pdf files to agent/ui/knowledge/ and rerun index build."
        )

    # all_chunks will hold the searchable pieces of text.
    # indexed_files will record which source files were indexed.
    all_chunks: list[dict[str, Any]] = []
    indexed_files: list[dict[str, str]] = []

    for doc in documents:
        # For each file, remember where it came from, then split its text into smaller searchable pieces.
        indexed_files.append(
            {
                "source_path": str(doc["source_path"]),
                "source_name": str(doc["source_name"]),
                "file_sha256": str(doc["file_sha256"]),
            }
        )
        all_chunks.extend(chunk_document(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap))

    if not all_chunks:
        # If documents were found but no chunks were created, something is wrong with the text extraction or chunking.
        raise ValueError(
            "Documents were found but no chunks were created. "
            "Check document text content and chunking settings."
        )

    # Convert every chunk into search tokens for BM25.
    tokenized_corpus = [_tokenize(chunk["text"]) for chunk in all_chunks]
    # Build the BM25 search index from the tokenized chunks.
    bm25 = BM25Okapi(tokenized_corpus)

    # These are the three files needed for retrieval and auditing.
    chunks_path = storage_path / "chunks.jsonl"
    bm25_path = storage_path / "bm25.pkl"
    manifest_path = storage_path / "manifest.json"

    # Save the searchable text chunks.
    _save_chunks_jsonl(all_chunks, chunks_path)

    # Save the BM25 index so retrieval can run later without rebuilding.
    with bm25_path.open("wb") as handle:
        # Persist the BM25 object so retrieval can run without rebuilding each session.
        pickle.dump(bm25, handle)

    # Create an audit record describing exactly what was indexed and how.
    manifest = {
        "build_timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "knowledge_directory": str(knowledge_path.resolve()),
        "storage_directory": str(storage_path.resolve()),
        "chunk_size": chunk_size,
        "chunk_overlap": chunk_overlap,
        "supported_extensions": sorted(list(SUPPORTED_EXTENSIONS)),
        "indexed_files": indexed_files,
        "num_chunks": len(all_chunks),
    }

    # Save the index-build summary for inspection and debugging.
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    # Return a short build summary for notebooks, scripts, or command-line use.
    return {
        "num_files_indexed": len(indexed_files),
        "num_chunks_created": len(all_chunks),
        "chunks_path": str(chunks_path.resolve()),
        "bm25_path": str(bm25_path.resolve()),
        "manifest_path": str(manifest_path.resolve()),
    }

# Allow this file to be run directly as a script.
if __name__ == "__main__":
    summary = build_local_index()
    print(json.dumps(summary, indent=2))
