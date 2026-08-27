"""
PASHA-NEURO-RAG Cross-Encoder Reranker
Author: Mohammad Subhan Pasha

Supports BGE-Reranker (sentence-transformers / HuggingFace) with Cohere Rerank API integration.
"""

import logging
from typing import List, Tuple, Optional
from neuro_rag.config import settings
from neuro_rag.ingestion.schemas import Chunk

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or settings.RERANKER_MODEL
        self._encoder_model = None
        self._cohere_client = None

    def _init_cohere(self):
        if settings.COHERE_API_KEY and not self._cohere_client:
            try:
                import cohere
                self._cohere_client = cohere.Client(settings.COHERE_API_KEY)
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere client: {e}")

    def _init_bge(self):
        if not self._encoder_model:
            try:
                from sentence_transformers import CrossEncoder
                self._encoder_model = CrossEncoder(self.model_name, max_length=512)
            except Exception as e:
                logger.warning(f"Could not load HuggingFace CrossEncoder model {self.model_name}: {e}")

    def rerank(self, query: str, chunks: List[Chunk], top_k: int = 5) -> List[Chunk]:
        if not chunks:
            return []

        # Try Cohere API if key is present
        if settings.COHERE_API_KEY:
            try:
                self._init_cohere()
                if self._cohere_client:
                    texts = [c.content for c in chunks]
                    response = self._cohere_client.rerank(
                        model="rerank-english-v3.0",
                        query=query,
                        documents=texts,
                        top_n=top_k
                    )
                    reranked_chunks = []
                    for result in response.results:
                        c = chunks[result.index]
                        c.metadata.semantic_score = float(result.relevance_score)
                        reranked_chunks.append(c)
                    return reranked_chunks
            except Exception as e:
                logger.warning(f"Cohere rerank failed: {e}. Falling back to BGE cross-encoder / heuristic scoring.")

        # Try BGE CrossEncoder local model
        try:
            self._init_bge()
            if self._encoder_model:
                pairs = [[query, c.content] for c in chunks]
                scores = self._encoder_model.predict(pairs)
                ranked_pairs = sorted(zip(chunks, scores), key=lambda x: x[1], reverse=True)
                reranked_chunks = []
                for chunk, score in ranked_pairs[:top_k]:
                    chunk.metadata.semantic_score = float(score)
                    reranked_chunks.append(chunk)
                return reranked_chunks
        except Exception as e:
            logger.warning(f"BGE CrossEncoder prediction failed: {e}. Using fallback term-frequency scoring.")

        # Fallback scoring when heavy neural models are not downloaded/available in test environment
        return self._heuristic_rerank(query, chunks, top_k)

    def _heuristic_rerank(self, query: str, chunks: List[Chunk], top_k: int) -> List[Chunk]:
        query_terms = set(query.lower().split())
        scored_chunks = []
        for chunk in chunks:
            words = chunk.content.lower().split()
            matches = sum(1 for w in words if w in query_terms)
            score = (matches / (len(query_terms) + 1e-5)) + (chunk.metadata.semantic_score or 0.0) * 0.5
            chunk.metadata.semantic_score = float(score)
            scored_chunks.append((chunk, score))

        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        return [c for c, s in scored_chunks[:top_k]]
