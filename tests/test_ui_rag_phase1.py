"""Basic tests for experimental local knowledge base (RAG Phase 1)."""

from __future__ import annotations

from pathlib import Path
import sys

# Ensure project root is importable for namespace package imports.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.ui.rag.chunking import chunk_text_words
from agent.ui.rag.loaders import load_documents
from agent.ui.rag.build_index import build_local_index
from agent.ui.rag.retrieve import retrieve


def test_chunking_overlap_behavior() -> None:
    text = " ".join(f"w{i}" for i in range(30))
    chunks = chunk_text_words(text, chunk_size=10, chunk_overlap=2)
    assert len(chunks) == 4
    assert chunks[0].split()[:3] == ["w0", "w1", "w2"]
    assert chunks[1].split()[:3] == ["w8", "w9", "w10"]


def test_load_txt_and_md_documents(tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    knowledge.mkdir(parents=True)
    (knowledge / "a.txt").write_text("alpha beta gamma", encoding="utf-8")
    (knowledge / "b.md").write_text("# Header\nchemistry model notes", encoding="utf-8")

    docs = load_documents(knowledge)
    names = sorted(d["source_name"] for d in docs)

    assert names == ["a.txt", "b.md"]
    assert all(d["file_sha256"] for d in docs)


def test_build_index_from_sample_documents(tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    storage = tmp_path / "storage"
    knowledge.mkdir(parents=True)

    (knowledge / "chem.txt").write_text(
        "Catalyst design for hydrogenation and adsorption studies.",
        encoding="utf-8",
    )
    (knowledge / "notes.md").write_text(
        "Descriptor relevance and robust model validation in chemistry.",
        encoding="utf-8",
    )

    summary = build_local_index(knowledge_dir=knowledge, storage_dir=storage, chunk_size=20, chunk_overlap=5)

    assert summary["num_files_indexed"] == 2
    assert summary["num_chunks_created"] >= 2
    assert Path(summary["chunks_path"]).exists()
    assert Path(summary["bm25_path"]).exists()
    assert Path(summary["manifest_path"]).exists()


def test_retrieve_relevant_chunk(tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    storage = tmp_path / "storage"
    knowledge.mkdir(parents=True)

    (knowledge / "kinetics.txt").write_text(
        "Reaction kinetics and activation energy are central to this analysis.",
        encoding="utf-8",
    )
    (knowledge / "random.txt").write_text(
        "Unrelated discussion about rainfall and travel plans.",
        encoding="utf-8",
    )

    build_local_index(knowledge_dir=knowledge, storage_dir=storage, chunk_size=30, chunk_overlap=5)
    results = retrieve("activation energy kinetics", k=1, storage_dir=storage)

    assert len(results) == 1
    assert results[0]["source_name"] == "kinetics.txt"
