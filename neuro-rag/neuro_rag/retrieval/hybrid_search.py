"""
PASHA-NEURO-RAG Hybrid Search Engine (BM25 + Dense Vector + RRF + Cross-Encoder Reranking)
Author: Mohammad Subhan Pasha
"""

from typing import List, Dict
from neuro_rag.config import settings
from neuro_rag.ingestion.schemas import Chunk
from neuro_rag.retrieval.vector_store import VectorStoreManager
from neuro_rag.retrieval.bm25_retriever import BM25Retriever
from neuro_rag.retrieval.reranker import CrossEncoderReranker


class HybridSearchEngine:
    """
    Executes dense vector search and BM25 sparse search, fuses results via
    Reciprocal Rank Fusion (RRF), and applies Cross-Encoder reranking.
    """

    def __init__(self, vector_store: VectorStoreManager, bm25_retriever: BM25Retriever):
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever
        self.reranker = CrossEncoderReranker()
        self.rrf_k = settings.RRF_K

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Chunk],
        sparse_results: List[Chunk],
        top_k: int = 10
    ) -> List[Chunk]:
        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        # Dense ranks
        for rank, chunk in enumerate(dense_results, start=1):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sparse ranks
        for rank, chunk in enumerate(sparse_results, start=1):
            cid = chunk.chunk_id
            chunk_map[cid] = chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort by RRF score
        sorted_cids = sorted(rrf_scores.keys(), key=lambda cid: rrf_scores[cid], reverse=True)

        fused_chunks = []
        for cid in sorted_cids[:top_k]:
            c = chunk_map[cid]
            c.metadata.semantic_score = rrf_scores[cid]
            fused_chunks.append(c)

        return fused_chunks

    def hybrid_search(
        self,
        query: str,
        top_k_retrieval: int = settings.TOP_K_RETRIEVAL,
        top_k_rerank: int = settings.TOP_K_RERANK
    ) -> List[Chunk]:
        # 1. Dense retrieval
        dense_chunks = self.vector_store.search(query, top_k=top_k_retrieval)

        # 2. Sparse BM25 retrieval
        sparse_chunks = self.bm25_retriever.search(query, top_k=top_k_retrieval)

        # 3. Reciprocal Rank Fusion
        fused_chunks = self._reciprocal_rank_fusion(dense_chunks, sparse_chunks, top_k=top_k_retrieval)

        # 4. Cross-Encoder Reranking
        final_chunks = self.reranker.rerank(query, fused_chunks, top_k=top_k_rerank)

        return final_chunks
