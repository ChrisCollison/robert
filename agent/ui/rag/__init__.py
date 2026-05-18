"""Local knowledge-base utilities (Phase 1 experimental).

This package provides local-only document loading, chunking,
BM25 index building, and retrieval helpers.
"""

from .build_index import build_local_index
from .retrieve import retrieve, build_context

__all__ = ["build_local_index", "retrieve", "build_context"]
