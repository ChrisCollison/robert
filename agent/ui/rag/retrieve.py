"""Retrieve top chunks from local BM25 index."""

from __future__ import annotations

import json
import pickle
import re
from pathlib import Path
from typing import Any


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_path(path_like: Path | str) -> Path:
    path = Path(path_like)
    if path.is_absolute():
        return path

    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    return (_project_root() / path).resolve()


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _load_chunks(chunks_path: Path) -> list[dict[str, Any]]:
    chunks: list[dict[str, Any]] = []
    with chunks_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                chunks.append(json.loads(line))
    return chunks


def retrieve(
    query: str,
    k: int = 5,
    storage_dir: Path | str = "agent/ui/storage",
) -> list[dict[str, Any]]:
    """Return top-k chunks for a query from the local BM25 index."""
    if not query or not query.strip():
        return []

    storage_path = _resolve_path(storage_dir)
    chunks_path = storage_path / "chunks.jsonl"
    bm25_path = storage_path / "bm25.pkl"

    if not chunks_path.exists() or not bm25_path.exists():
        raise FileNotFoundError(
            "Local index not found. Run agent/ui/Build_Local_Knowledge_Index.ipynb first."
        )

    chunks = _load_chunks(chunks_path)
    if not chunks:
        raise ValueError(
            "No chunks found in index. If knowledge folder is empty, add files and rebuild index."
        )

    with bm25_path.open("rb") as handle:
        bm25 = pickle.load(handle)

    query_tokens = _tokenize(query)
    scores = bm25.get_scores(query_tokens)

    ranked_indices = sorted(
        range(len(scores)),
        key=lambda idx: float(scores[idx]),
        reverse=True,
    )[: max(1, k)]

    results: list[dict[str, Any]] = []
    for idx in ranked_indices:
        chunk = chunks[idx]
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


def build_context(results: list[dict[str, Any]]) -> str:
    """Format retrieval results into a context block for later LLM use."""
    blocks: list[str] = []
    for i, item in enumerate(results, start=1):
        source_name = item.get("source_name", "unknown")
        chunk_index = item.get("chunk_index", "?")
        text = str(item.get("text", "")).strip()
        blocks.append(f"[Source {i}: {source_name} | chunk {chunk_index}]\n{text}")
    return "\n\n".join(blocks)
