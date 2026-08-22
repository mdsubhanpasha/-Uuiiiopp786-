"""Naive RAG Engine implementation.

Uses dense vector embeddings with cosine similarity for top-K document
retrieval and context-augmented prompt synthesis.
"""

import json
import logging
import math
import os
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NaiveRAG")


class NaiveRAG:
    """Naive Dense Vector Retrieval-Augmented Generation Engine."""

    def __init__(
        self,
        corpus_path: Optional[str] = None,
        embedding_dim: int = 384,
    ) -> None:
        """Initialize NaiveRAG instance.

        Args:
            corpus_path: Path to sample corpus JSON file.
            embedding_dim: Vector embedding dimensionality.
        """
        self.embedding_dim = embedding_dim
        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []

        if corpus_path and os.path.exists(corpus_path):
            self.load_corpus(corpus_path)

    def _generate_embedding(self, text: str) -> List[float]:
        """Generate a deterministic normalized vector embedding for text.

        Args:
            text: Input string to embed.

        Returns:
            Normalized list of floats representing vector embedding.
        """
        vec = [0.0] * self.embedding_dim
        words = text.lower().split()
        if not words:
            return vec

        for idx, word in enumerate(words):
            hash_val = sum(ord(c) for c in word)
            slot = hash_val % self.embedding_dim
            vec[slot] += math.log(idx + 2) + len(word)

        norm = math.sqrt(sum(v * v for v in vec))
        if norm > 1e-9:
            vec = [v / norm for v in vec]
        return vec

    def _cosine_similarity(
        self, vec1: List[float], vec2: List[float]
    ) -> float:
        """Compute cosine similarity between two vectors.

        Args:
            vec1: First vector.
            vec2: Second vector.

        Returns:
            Float representing cosine similarity.
        """
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        if norm1 <= 1e-9 or norm2 <= 1e-9:
            return 0.0
        return dot / (norm1 * norm2)

    def load_corpus(self, filepath: str) -> None:
        """Load and index documents from JSON file.

        Args:
            filepath: Path to corpus file.
        """
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.documents = data
        self.embeddings = [
            self._generate_embedding(
                f"{doc.get('title', '')} {doc.get('content', '')}"
            )
            for doc in self.documents
        ]
        logger.info(
            "Loaded and indexed %d documents in NaiveRAG.",
            len(self.documents),
        )

    def retrieve(
        self, query: str, top_k: int = 3
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Retrieve top-K relevant documents using dense cosine similarity.

        Args:
            query: User search query.
            top_k: Number of documents to retrieve.

        Returns:
            List of tuples (document_dict, similarity_score).
        """
        if not self.documents:
            return []

        query_vec = self._generate_embedding(query)
        scored_docs: List[Tuple[Dict[str, Any], float]] = []

        for doc, doc_vec in zip(self.documents, self.embeddings):
            score = self._cosine_similarity(query_vec, doc_vec)
            scored_docs.append((doc, score))

        scored_docs.sort(key=lambda x: x[1], reverse=True)
        return scored_docs[:top_k]

    def generate(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Execute end-to-end Naive RAG retrieval and generation.

        Args:
            query: User query.
            top_k: Top K context documents.

        Returns:
            Dict containing paradigm name, retrieved contexts, and answer.
        """
        results = self.retrieve(query, top_k=top_k)
        contexts = [doc["content"] for doc, _ in results]

        context_str = "\n".join(
            f"[{i+1}] {content}" for i, content in enumerate(contexts)
        )
        answer = (
            f"[Naive RAG Response]\nBased on retrieved context:\n"
            f"{context_str}\nSynthesized Answer for query '{query}': "
            f"Retrieved across top {len(results)} context documents."
        )

        return {
            "paradigm": "Naive RAG",
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
            "response": answer,
        }
