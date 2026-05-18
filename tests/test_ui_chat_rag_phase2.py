"""Tests for Phase 2 local RAG integration in chat routing."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.ui.chat import answer_question
from agent.ui.rag.build_index import build_local_index


def test_answer_question_uses_local_rag_without_api_key(monkeypatch, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    storage = tmp_path / "storage"
    knowledge.mkdir(parents=True)

    (knowledge / "glossary.md").write_text(
        "Adsorption and desorption are core surface chemistry concepts.",
        encoding="utf-8",
    )

    build_local_index(knowledge_dir=knowledge, storage_dir=storage, chunk_size=30, chunk_overlap=5)

    monkeypatch.setenv("ROBERT_ENABLE_LOCAL_RAG", "true")
    monkeypatch.setenv("ROBERT_RAG_STORAGE_DIR", str(storage))
    monkeypatch.setenv("ROBERT_RAG_TOP_K", "2")

    result = answer_question(
        user_question="What does adsorption mean in this context?",
        run_context={"predict": {}, "verify": {}},
        diagnosis_json={},
        api_key=None,
    )

    assert result["source"] == "local-rag"
    assert "local knowledge snippets" in result["content"].lower()
    assert "glossary.md" in result["content"]


def test_answer_question_falls_back_when_local_index_missing(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ROBERT_ENABLE_LOCAL_RAG", "true")
    monkeypatch.setenv("ROBERT_RAG_STORAGE_DIR", str(tmp_path / "missing_storage"))

    result = answer_question(
        user_question="Tell me more about this model behavior",
        run_context={"predict": {}, "verify": {}},
        diagnosis_json={},
        api_key=None,
    )

    assert result["source"] == "no-api-key"
    assert "did not match a deterministic faq rule" in result["content"].lower()


def test_answer_question_respects_session_override_disable(monkeypatch, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    storage = tmp_path / "storage"
    knowledge.mkdir(parents=True)

    (knowledge / "chem.txt").write_text(
        "Catalyst selectivity and adsorption descriptors are discussed here.",
        encoding="utf-8",
    )

    build_local_index(knowledge_dir=knowledge, storage_dir=storage, chunk_size=30, chunk_overlap=5)

    monkeypatch.setenv("ROBERT_ENABLE_LOCAL_RAG", "true")
    monkeypatch.setenv("ROBERT_RAG_STORAGE_DIR", str(storage))

    result = answer_question(
        user_question="What is adsorption?",
        run_context={"predict": {}, "verify": {}},
        diagnosis_json={},
        api_key=None,
        use_local_rag=False,
    )

    assert result["source"] == "no-api-key"


def test_score_question_includes_score_and_local_context(monkeypatch, tmp_path: Path) -> None:
    knowledge = tmp_path / "knowledge"
    storage = tmp_path / "storage"
    knowledge.mkdir(parents=True)

    (knowledge / "faq.md").write_text(
        "A low ROBERT score often indicates data limitations, descriptor mismatch, or split difficulty.",
        encoding="utf-8",
    )

    build_local_index(knowledge_dir=knowledge, storage_dir=storage, chunk_size=30, chunk_overlap=5)

    monkeypatch.setenv("ROBERT_ENABLE_LOCAL_RAG", "true")
    monkeypatch.setenv("ROBERT_RAG_STORAGE_DIR", str(storage))

    run_context = {
        "pred_type": "reg",
        "score": {"no_pfi": 4.0, "pfi": 3.5},
        "predict": {
            "no_pfi": {
                "r2_cv": 0.61,
                "r2_test": 0.55,
                "rmse_cv": 0.42,
                "rmse_test": 0.48,
                "n_train": 40,
                "n_test": 10,
                "n_descriptors": 12,
                "descriptors": ["d1", "d2"],
                "points_descp_ratio": "40:12",
            },
            "pfi": {"r2_test": 0.50},
        },
        "verify": {"no_pfi": {"passed_tests": 3, "failed_tests": 0, "unclear_tests": 0}},
    }
    diagnosis_json = {
        "observations": {
            "no_pfi": [
                {
                    "key": "interp_cv_optimistic",
                    "level": "warning",
                    "message": "CV appears optimistic relative to test performance.",
                }
            ]
        }
    }

    result = answer_question(
        user_question="Why did I get this score?",
        run_context=run_context,
        diagnosis_json=diagnosis_json,
        api_key=None,
    )

    assert result["source"] == "heuristic"
    assert "ROBERT Score (No PFI / PFI): 4.0 / 3.5" in result["content"]
    assert "Related local knowledge snippets" in result["content"]
    assert "faq.md" in result["content"]
