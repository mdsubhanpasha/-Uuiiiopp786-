"""Hybrid / Modular RAG Engine implementation.

Combines BM25 lexical search and Dense vector search, merged using
Reciprocal Rank Fusion (RRF) and Cohere reranking simulation.
"""

import json
import logging
import math
import os
from typing import Any, Dict, List, Optional, Tuple

try:
    from rank_bm25 import BM25Okapi
except ImportError:
    BM25Okapi = None

from src.naive_rag import NaiveRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("HybridRAG")


class HybridRAG:
    """Hybrid RAG combining Lexical (BM25) and Dense Vector retrieval."""

    def __init__(
        self,
        corpus_path: Optional[str] = None,
        rrf_k: int = 60,
    ) -> None:
        """Initialize HybridRAG instance.

        Args:
            corpus_path: Path to sample corpus JSON file.
            rrf_k: Smoothing constant for Reciprocal Rank Fusion.
        """
        self.rrf_k = rrf_k
        self.documents: List[Dict[str, Any]] = []
        self.dense_engine = NaiveRAG()
        self.bm25: Any = None
        self.tokenized_corpus: List[List[str]] = []

        if corpus_path and os.path.exists(corpus_path):
            self.load_corpus(corpus_path)

    def load_corpus(self, filepath: str) -> None:
        """Load corpus for both BM25 lexical search and dense vector search.

        Args:
            filepath: Path to corpus JSON file.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        self.dense_engine.load_corpus(filepath)

        self.tokenized_corpus = [
            f"{doc.get('title', '')} {doc.get('content', '')}".lower().split()
            for doc in self.documents
        ]
        if BM25Okapi is not None and self.tokenized_corpus:
            self.bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info(
            "Loaded and indexed %d documents in HybridRAG.",
            len(self.documents),
        )

    def _bm25_search(
        self, query: str, top_k: int
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Perform BM25 lexical search.

        Args:
            query: Input search query.
            top_k: Number of results to retrieve.

        Returns:
            List of (doc_dict, score) tuples.
        """
        if not self.documents:
            return []

        tokenized_query = query.lower().split()
        if self.bm25 is not None:
            scores = self.bm25.get_scores(tokenized_query)
        else:
            scores = []
            for doc_tokens in self.tokenized_corpus:
                cnt = sum(doc_tokens.count(q) for q in tokenized_query)
                scores.append(float(cnt))

        indexed_scores = list(enumerate(scores))
        indexed_scores.sort(key=lambda x: x[1], reverse=True)

        return [
            (self.documents[idx], score)
            for idx, score in indexed_scores[:top_k]
        ]

    def reciprocal_rank_fusion(
        self,
        dense_results: List[Tuple[Dict[str, Any], float]],
        lexical_results: List[Tuple[Dict[str, Any], float]],
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Combine dense and lexical results using Reciprocal Rank Fusion.

        Args:
            dense_results: Dense vector retrieval results.
            lexical_results: Lexical BM25 retrieval results.

        Returns:
            Fused list of (doc, rrf_score) tuples.
        """
        rrf_scores: Dict[str, float] = {}
        doc_map: Dict[str, Dict[str, Any]] = {}

        for rank, (doc, _) in enumerate(dense_results, start=1):
            doc_id = doc.get("id", str(id(doc)))
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (
                1.0 / (self.rrf_k + rank)
            )

        for rank, (doc, _) in enumerate(lexical_results, start=1):
            doc_id = doc.get("id", str(id(doc)))
            doc_map[doc_id] = doc
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + (
                1.0 / (self.rrf_k + rank)
            )

        fused = [
            (doc_map[doc_id], score) for doc_id, score in rrf_scores.items()
        ]
        fused.sort(key=lambda x: x[1], reverse=True)
        return fused

    def cohere_rerank_simulation(
        self, query: str, candidates: List[Tuple[Dict[str, Any], float]]
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Simulate Cohere reranking over retrieved candidate docs.

        Args:
            query: Input user query.
            candidates: Fused doc candidates with RRF scores.

        Returns:
            Reranked list of (doc, rerank_score).
        """
        query_words = set(query.lower().split())
        reranked: List[Tuple[Dict[str, Any], float]] = []

        for doc, rrf_score in candidates:
            content_words = doc.get("content", "").lower().split()
            title_words = doc.get("title", "").lower().split()

            overlap_content = sum(
                1 for w in query_words if w in content_words
            )
            overlap_title = sum(1 for w in query_words if w in title_words)

            cross_encoder_score = (
                (rrf_score * 50.0)
                + (overlap_content * 0.3)
                + (overlap_title * 0.5)
            )

            final_score = 1.0 / (1.0 + math.exp(-cross_encoder_score))
            reranked.append((doc, float(final_score)))

        reranked.sort(key=lambda x: x[1], reverse=True)
        return reranked

    def retrieve(
        self, query: str, top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve top-K documents using Hybrid RAG with RRF and reranking.

        Args:
            query: User query.
            top_k: Top K final results.

        Returns:
            List of (doc, final_score) tuples.
        """
        dense_res = self.dense_engine.retrieve(query, top_k=top_k * 2)
        lexical_res = self._bm25_search(query, top_k=top_k * 2)

        fused_res = self.reciprocal_rank_fusion(dense_res, lexical_res)
        reranked_res = self.cohere_rerank_simulation(query, fused_res)

        return reranked_res[:top_k]

    def generate(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Execute end-to-end Hybrid RAG pipeline.

        Args:
            query: User search query.
            top_k: Top documents to retrieve and rerank.

        Returns:
            Dict containing paradigm details and generated response.
        """
        results = self.retrieve(query, top_k=top_k)
        contexts = [
            f"[{i+1}] {doc['title']}: {doc['content']}"
            for i, (doc, _) in enumerate(results)
        ]

        response_text = (
            "[Hybrid Modular RAG Response]\n"
            "Hybrid search combining BM25 Lexical + Dense Vector with RRF "
            "& Cohere Reranker:\n"
            + "\n".join(contexts)
            + f"\n\nSynthesized Analysis for '{query}': High-precision match."
        )

        return {
            "paradigm": "Hybrid / Modular RAG",
            "query": query,
            "retrieved_documents": [
                {
                    "id": doc.get("id"),
                    "title": doc.get("title"),
                    "score": round(score, 4),
                    "content": doc.get("content"),
                }
                for doc, score in results
            ],
            "response": response_text,
        }
