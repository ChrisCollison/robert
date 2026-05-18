"""Word-based chunking helpers for local knowledge indexing."""

from __future__ import annotations

from typing import Any


def chunk_text_words(text: str, chunk_size: int = 900, chunk_overlap: int = 150) -> list[str]:
    """Split text into overlapping word chunks."""
    if chunk_size <= 0:
        raise ValueError("chunk_size must be > 0")
    if chunk_overlap < 0:
        raise ValueError("chunk_overlap must be >= 0")
    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    words = text.split()
    if not words:
        return []

    step = chunk_size - chunk_overlap
    chunks: list[str] = []
    for start in range(0, len(words), step):
        end = start + chunk_size
        chunk_words = words[start:end]
        if not chunk_words:
            break
        chunks.append(" ".join(chunk_words))
        if end >= len(words):
            break

    return chunks


def chunk_document(
    document: dict[str, Any],
    chunk_size: int = 900,
    chunk_overlap: int = 150,
) -> list[dict[str, Any]]:
    """Chunk one loaded document into chunk records."""
    text = str(document.get("text", ""))
    source_path = str(document.get("source_path", ""))
    source_name = str(document.get("source_name", ""))
    file_sha256 = str(document.get("file_sha256", ""))

    chunks = chunk_text_words(text=text, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

    records: list[dict[str, Any]] = []
    for idx, chunk_text in enumerate(chunks):
        records.append(
            {
                "chunk_id": f"{file_sha256[:12]}_{idx}",
                "source_path": source_path,
                "source_name": source_name,
                "chunk_index": idx,
                "text": chunk_text,
                "file_sha256": file_sha256,
            }
        )
    return records
