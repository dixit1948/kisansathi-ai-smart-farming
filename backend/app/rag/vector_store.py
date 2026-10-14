"""
RAG Vector Store — ChromaDB backend with BM25 hybrid retrieval.
Interface is swappable to watsonx.data/Milvus.
"""
from typing import Optional
import structlog
from app.core.config import settings
from app.core.granite import get_granite_client

logger = structlog.get_logger(__name__)


class VectorStore:
    """
    Manages ChromaDB collection for knowledge retrieval.
    Hybrid: vector similarity + BM25 keyword scoring, re-ranked by combined score.
    """

    def __init__(self):
        self._collection = None
        self._bm25 = None
        self._all_docs: list[dict] = []  # local cache for BM25
        self._init_chroma()

    def _init_chroma(self):
        try:
            import chromadb
            client = chromadb.HttpClient(host=settings.CHROMA_HOST, port=settings.CHROMA_PORT)
            client.heartbeat()
            self._collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info("ChromaDB connected", collection=settings.CHROMA_COLLECTION,
                        count=self._collection.count())
        except Exception as e:
            logger.warning("ChromaDB unavailable — RAG will return empty results", error=str(e))
            self._collection = None

    async def add_documents(self, documents: list[dict]) -> int:
        """
        Add chunked documents. Each doc: {id, text, metadata}.
        Returns count added.
        """
        if not self._collection:
            logger.warning("ChromaDB not available — skipping add_documents")
            return 0

        granite = get_granite_client()
        texts = [d["text"] for d in documents]
        embeddings = await granite.embed(texts)

        valid = [(d, e) for d, e in zip(documents, embeddings) if e]
        if not valid:
            return 0

        self._collection.add(
            ids=[d["id"] for d, _ in valid],
            embeddings=[e for _, e in valid],
            documents=[d["text"] for d, _ in valid],
            metadatas=[d.get("metadata", {}) for d, _ in valid],
        )
        # Update BM25 corpus
        self._all_docs.extend(documents)
        self._rebuild_bm25()
        logger.info("Documents added to ChromaDB", count=len(valid))
        return len(valid)

    def _rebuild_bm25(self):
        try:
            from rank_bm25 import BM25Okapi
            corpus = [d["text"].lower().split() for d in self._all_docs]
            self._bm25 = BM25Okapi(corpus)
        except Exception:
            self._bm25 = None

    async def retrieve(
        self,
        query: str,
        n_results: int = 5,
        crop_filter: Optional[str] = None,
        similarity_threshold: float = 0.3,
    ) -> list[dict]:
        """
        Hybrid retrieval: vector + BM25 fusion. Returns top chunks with scores and metadata.
        """
        if not self._collection or self._collection.count() == 0:
            logger.warning("No documents in ChromaDB — returning empty retrieval")
            return _get_sample_fallback(query, crop_filter)

        granite = get_granite_client()
        query_embed = await granite.embed([query])
        query_vec = query_embed[0] if query_embed and query_embed[0] else None

        where = {"crop": crop_filter} if crop_filter else None
        vector_results = self._collection.query(
            query_embeddings=[query_vec] if query_vec else None,
            query_texts=[query] if not query_vec else None,
            n_results=min(n_results * 2, max(self._collection.count(), 1)),
            where=where,
            include=["documents", "metadatas", "distances"],
        )

        chunks = []
        if vector_results and vector_results.get("ids"):
            for i, doc_id in enumerate(vector_results["ids"][0]):
                distance = vector_results["distances"][0][i]
                similarity = 1 - distance  # cosine
                if similarity >= similarity_threshold:
                    chunks.append({
                        "id": doc_id,
                        "text": vector_results["documents"][0][i],
                        "metadata": vector_results["metadatas"][0][i],
                        "vector_score": similarity,
                    })

        # BM25 re-ranking
        if self._bm25 and self._all_docs:
            bm25_scores = self._bm25.get_scores(query.lower().split())
            for chunk in chunks:
                # Find BM25 score for this chunk's text
                try:
                    idx = next(i for i, d in enumerate(self._all_docs) if d["id"] == chunk["id"])
                    chunk["bm25_score"] = float(bm25_scores[idx])
                except StopIteration:
                    chunk["bm25_score"] = 0.0
            # Normalize and combine
            max_bm25 = max((c["bm25_score"] for c in chunks), default=1.0) or 1.0
            for chunk in chunks:
                chunk["combined_score"] = 0.7 * chunk["vector_score"] + 0.3 * (chunk["bm25_score"] / max_bm25)
        else:
            for chunk in chunks:
                chunk["combined_score"] = chunk["vector_score"]

        chunks.sort(key=lambda x: x["combined_score"], reverse=True)
        return chunks[:n_results]


def _get_sample_fallback(query: str, crop: Optional[str]) -> list[dict]:
    """Return hardcoded sample chunks when ChromaDB is empty (demo fallback)."""
    return [
        {
            "id": "sample_1",
            "text": "Cotton requires well-drained black soil. Sow in June-July. Apply 120kg N, 60kg P2O5 per hectare. Water every 10-14 days depending on soil type. [Sample ICAR-CICR Guide]",
            "metadata": {"source": "ICAR-CICR Cotton Guide (Sample)", "crop": "cotton", "topic": "cultivation", "page": "12", "is_sample": True},
            "vector_score": 0.7, "bm25_score": 0.5, "combined_score": 0.64,
        },
        {
            "id": "sample_2",
            "text": "Groundnut sowing season: Kharif (June-July), Rabi (Oct-Nov). Seed rate: 100 kg/ha for bunch, 80 kg/ha for spreading varieties. Requires sandy loam soil, pH 6.0-6.5. [Sample KVK Advisory]",
            "metadata": {"source": "KVK Advisory Gujarat (Sample)", "crop": "groundnut", "topic": "cultivation", "page": "5", "is_sample": True},
            "vector_score": 0.65, "bm25_score": 0.4, "combined_score": 0.575,
        },
        {
            "id": "sample_3",
            "text": "Wheat sowing in Gujarat: Rabi season (Nov 1-15). Variety GW-496 recommended for South Gujarat. Seed rate: 100 kg/ha. First irrigation at Crown Root Initiation (25 DAS). [Sample State Agriculture Dept]",
            "metadata": {"source": "State Agri Dept Gujarat (Sample)", "crop": "wheat", "topic": "sowing", "page": "3", "is_sample": True},
            "vector_score": 0.6, "bm25_score": 0.35, "combined_score": 0.525,
        },
    ]


# Singleton
_vector_store: Optional[VectorStore] = None


def get_vector_store() -> VectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = VectorStore()
    return _vector_store
