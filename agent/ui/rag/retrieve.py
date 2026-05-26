"""Retrieve top chunks from local BM25 index."""
# This file searches the local knowledge-base index.
# It finds the text chunks that best match a user question.

from __future__ import annotations

import json
import pickle
import re
from pathlib import Path
from typing import Any

# Find the main project folder by walking upward from this file.
def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]

# Convert a user-provided path into a full path.
# This makes the code work from notebooks, scripts, or the app.
def _resolve_path(path_like: Path | str) -> Path:
    path = Path(path_like)
    if path.is_absolute():
        return path

    # Favor caller-relative paths first for notebook runs from different working dirs.
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    return (_project_root() / path).resolve()

# Break text into simple lowercase search terms.
# This prepares the question for keyword search.
def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())

# Load the saved knowledge-base chunks from chunks.jsonl.
# Each line is one text chunk plus its source information.
def _load_chunks(chunks_path: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    with chunks_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks

# Given a user question, return the top k most relevant chunks
# from the local knowledge base.
def retrieve(
    query: str,
    k: int = 5,
    storage_dir: Path | str = "agent/ui/storage",
) -> list[dict[str, Any]]:
    """Return top-k chunks for a query from the local BM25 index."""
    # Do not search if the user question is empty.
    if not query or not query.strip():
        return []

    # Find the two files needed for retrieval:
    # 1. chunks.jsonl = the text chunks
    # 2. bm25.pkl = the keyword-search index
    storage_path = _resolve_path(storage_dir)
    chunks_path = storage_path / "chunks.jsonl"
    bm25_path = storage_path / "bm25.pkl"

    # If the index has not been built yet, stop and tell the user what to run.
    if not chunks_path.exists() or not bm25_path.exists():
        raise FileNotFoundError(
            "Local index not found. Run agent/ui/Build_Local_Knowledge_Index.ipynb first."
        )

    # Load all indexed chunks.
    # If there are no chunks, the knowledge folder was probably empty.
    chunks = _load_chunks(chunks_path)
    if not chunks:
        raise ValueError(
            "No chunks found in index. If knowledge folder is empty, add files and rebuild index."
        )

    # Load the saved BM25 search index.
    with bm25_path.open("rb") as handle:
        bm25 = pickle.load(handle)

    # Convert the user question into searchable words.
    query_tokens = _tokenize(query)
    # Score every chunk based on how well it matches the question.
    scores = bm25.get_scores(query_tokens)

    # Rank chunks from most relevant to least relevant.
    # Keep only the top k results.
    ranked_indices = sorted(
        range(len(scores)),
        key=lambda idx: float(scores[idx]),
        reverse=True,
    )[: max(1, k)]

    results: list[dict[str, Any]] = []
    for idx in ranked_indices:
        chunk = chunks[idx]
        # Package each result with its source information and text.
        # This keeps retrieval auditable.
        results.append(
            {
                "source_path": chunk.get("source_path"),
                "source_name": chunk.get("source_name"),
                "chunk_index": chunk.get("chunk_index"),
                "score": float(scores[idx]),
                "text": chunk.get("text", ""),
            }
        )

    return results

# Format retrieved chunks into one text block.
# This block can later be given to the LLM as background context.
# Source labels are kept so the answer can be traced back.
def build_context(results: list[dict[str, Any]]) -> str:
    """Format retrieval results into a context block for later LLM use."""
    blocks: list[str] = []
    for i, item in enumerate(results, start=1):
        source_name = item.get("source_name", "unknown")
        chunk_index = item.get("chunk_index", "?")
        text = str(item.get("text", "")).strip()
        # Keep source labels in the prompt context so answers remain auditable.
        blocks.append(f"[Source {i}: {source_name} | chunk {chunk_index}]\n{text}")
    return "\n\n".join(blocks)
