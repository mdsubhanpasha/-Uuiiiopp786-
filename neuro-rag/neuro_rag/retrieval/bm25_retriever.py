"""
PASHA-NEURO-RAG BM25 Sparse Keyword Retriever
Author: Mohammad Subhan Pasha
"""

import re
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from neuro_rag.ingestion.schemas import Chunk


class BM25Retriever:
    """
    BM25 sparse keyword retriever maintaining inverted index over chunk corpus.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Chunk] = []
        self.bm25: Optional[BM25Okapi] = None

    def _tokenize(self, text: str) -> List[str]:
        words = re.findall(r'\b\w+\b', text.lower())
        return words

    def index_chunks(self, chunks: List[Chunk]):
        self.chunks.extend(chunks)
        corpus_tokens = [self._tokenize(c.content) for c in self.chunks]
        self.bm25 = BM25Okapi(corpus_tokens, k1=self.k1, b=self.b)

    def search(self, query: str, top_k: int = 10) -> List[Chunk]:
        if not self.bm25 or not self.chunks:
            return []

        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.chunks[:top_k]

        scores = self.bm25.get_scores(query_tokens)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0.0 or len(results) < top_k:
                chunk = self.chunks[idx]
                chunk.metadata.semantic_score = float(scores[idx])
                results.append(chunk)

        return results
