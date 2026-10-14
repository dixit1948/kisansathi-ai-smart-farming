"""
RAG Retrieval unit tests — ChromaDB vector store with BM25 hybrid ranking.
"""
import pytest
from app.rag.vector_store import get_vector_store


@pytest.mark.asyncio
async def test_hybrid_rag_fallback_retrieval():
    """Verify hybrid RAG returns grounded documents even when ChromaDB is empty (demo fallback)."""
    vs = get_vector_store()
    results = await vs.retrieve(
        query="When should I sow cotton and what fertilizer to apply?",
        crop_filter="cotton",
        n_results=3,
    )
    assert len(results) > 0
    top = results[0]
    assert "text" in top
    assert "metadata" in top
    assert "source" in top["metadata"]
    assert "combined_score" in top
    assert top["combined_score"] > 0.0


@pytest.mark.asyncio
async def test_crop_filter_retrieval():
    """Verify RAG filter respects crop scoping."""
    vs = get_vector_store()
    results = await vs.retrieve(
        query="Sowing recommendations in Gujarat",
        crop_filter="wheat",
        n_results=2,
    )
    assert len(results) > 0
    assert any(c["metadata"].get("crop") == "wheat" for c in results)
