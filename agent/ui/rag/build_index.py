"""Build a local BM25 knowledge index (Phase 1 experimental)."""

from __future__ import annotations

import json
import pickle
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .chunking import chunk_document
from .loaders import SUPPORTED_EXTENSIONS, load_documents


def _project_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _resolve_path(path_like: Path | str) -> Path:
    path = Path(path_like)
    if path.is_absolute():
        return path

    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate

    root_candidate = (_project_root() / path).resolve()
    return root_candidate


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9_]+", text.lower())


def _save_chunks_jsonl(chunks: list[dict[str, Any]], out_path: Path) -> None:
    with out_path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=True) + "\n")


def build_local_index(
    knowledge_dir: Path | str = "agent/ui/knowledge",
    storage_dir: Path | str = "agent/ui/storage",
    chunk_size: int = 350,
    chunk_overlap: int = 75,
) -> dict[str, Any]:
    """Build a local BM25 index and persist artifacts to disk."""
    try:
        from rank_bm25 import BM25Okapi  # type: ignore
    except ImportError as exc:
        raise RuntimeError(
            "rank-bm25 is required. Install UI dependencies with: "
            "pip install -r requirements_ui.txt"
        ) from exc

    knowledge_path = _resolve_path(knowledge_dir)
    storage_path = _resolve_path(storage_dir)
    storage_path.mkdir(parents=True, exist_ok=True)

    documents = load_documents(knowledge_path)
    if not documents:
        raise ValueError(
            "No supported files found in knowledge folder. "
            "Add .txt, .md, or .pdf files to agent/ui/knowledge/ and rerun index build."
        )

    all_chunks: list[dict[str, Any]] = []
    indexed_files: list[dict[str, str]] = []

    for doc in documents:
        indexed_files.append(
            {
                "source_path": str(doc["source_path"]),
                "source_name": str(doc["source_name"]),
                "file_sha256": str(doc["file_sha256"]),
            }
        )
        all_chunks.extend(chunk_document(doc, chunk_size=chunk_size, chunk_overlap=chunk_overlap))

    if not all_chunks:
        raise ValueError(
            "Documents were found but no chunks were created. "
            "Check document text content and chunking settings."
        )

    tokenized_corpus = [_tokenize(chunk["text"]) for chunk in all_chunks]
    bm25 = BM25Okapi(tokenized_corpus)

    chunks_path = storage_path / "chunks.jsonl"
    bm25_path = storage_path / "bm25.pkl"
    manifest_path = storage_path / "manifest.json"

    _save_chunks_jsonl(all_chunks, chunks_path)

    with bm25_path.open("wb") as handle:
        pickle.dump(bm25, handle)

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

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return {
        "num_files_indexed": len(indexed_files),
        "num_chunks_created": len(all_chunks),
        "chunks_path": str(chunks_path.resolve()),
        "bm25_path": str(bm25_path.resolve()),
        "manifest_path": str(manifest_path.resolve()),
    }


if __name__ == "__main__":
    summary = build_local_index()
    print(json.dumps(summary, indent=2))
