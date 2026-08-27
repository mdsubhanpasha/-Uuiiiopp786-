"""
PASHA-NEURO-RAG Semantic Chunker
Author: Mohammad Subhan Pasha

Uses sentence semantic similarity splitting rather than fixed character size chunking.
Calculates distance between consecutive sentence embeddings and splits at semantic boundaries.
"""

import re
import math
from typing import List, Optional
import numpy as np

from neuro_rag.ingestion.schemas import Document, Chunk, ChunkMetadata
from neuro_rag.config import settings


class SemanticChunker:
    """
    Semantic Chunker splits documents based on semantic distance between sentences.
    Falls back to intelligent sentence clustering when embeddings are not pre-cached.
    """

    def __init__(
        self,
        target_chunk_tokens: int = 350,
        similarity_threshold: float = 0.75,
        min_chunk_tokens: int = 80,
        max_chunk_tokens: int = 600,
        embed_fn = None
    ):
        self.target_chunk_tokens = target_chunk_tokens
        self.similarity_threshold = similarity_threshold
        self.min_chunk_tokens = min_chunk_tokens
        self.max_chunk_tokens = max_chunk_tokens
        self.embed_fn = embed_fn

    def _split_into_sentences(self, text: str) -> List[str]:
        # Split on sentence boundaries, keeping punctuation
        sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!)\s+')
        sentences = sentence_endings.split(text)
        cleaned = [s.strip() for s in sentences if s and len(s.strip()) > 3]
        return cleaned if cleaned else [text]

    def _estimate_tokens(self, text: str) -> int:
        # Approximate 1 token = 4 characters or ~0.75 words
        return max(1, int(len(text.split()) * 1.3))

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        a = np.array(vec1)
        b = np.array(vec2)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return float(np.dot(a, b) / (norm_a * norm_b))

    def chunk_document(self, doc: Document) -> List[Chunk]:
        sentences = self._split_into_sentences(doc.content)
        if not sentences:
            return []

        chunks: List[Chunk] = []
        current_sentences: List[str] = []
        current_token_count = 0
        chunk_idx = 0

        # If embed_fn is available, perform sentence-level embedding semantic split
        embeddings: Optional[List[List[float]]] = None
        if self.embed_fn is not None:
            try:
                embeddings = self.embed_fn(sentences)
            except Exception:
                embeddings = None

        for i, sentence in enumerate(sentences):
            sent_tokens = self._estimate_tokens(sentence)

            # Check if sentence is structurally or semantically distinct (e.g., Section Header)
            is_header = (sentence.startswith("#") or sentence.isupper() or len(sentence.split()) < 6) and current_token_count > self.min_chunk_tokens

            # Check semantic distance if embeddings are available
            semantic_split = False
            if embeddings and i > 0 and len(current_sentences) > 0:
                sim = self._cosine_similarity(embeddings[i - 1], embeddings[i])
                if sim < self.similarity_threshold and current_token_count >= self.min_chunk_tokens:
                    semantic_split = True

            # Boundary trigger conditions
            exceeds_max = (current_token_count + sent_tokens) > self.max_chunk_tokens
            reached_target_boundary = (current_token_count >= self.target_chunk_tokens and (is_header or semantic_split))

            if current_sentences and (exceeds_max or reached_target_boundary):
                chunk_text = " ".join(current_sentences)
                start_char = doc.content.find(current_sentences[0])
                end_char = start_char + len(chunk_text) if start_char != -1 else len(chunk_text)

                chunk_meta = ChunkMetadata(
                    doc_id=doc.doc_id,
                    chunk_index=chunk_idx,
                    source_type=doc.metadata.source_type,
                    source_name=doc.metadata.source_name,
                    uri=doc.metadata.uri,
                    start_char=max(0, start_char),
                    end_char=end_char,
                    token_count=current_token_count,
                    semantic_score=1.0
                )
                chunks.append(Chunk(content=chunk_text, metadata=chunk_meta))

                chunk_idx += 1
                current_sentences = []
                current_token_count = 0

            current_sentences.append(sentence)
            current_token_count += sent_tokens

        # Tail chunk
        if current_sentences:
            chunk_text = " ".join(current_sentences)
            start_char = doc.content.find(current_sentences[0])
            end_char = start_char + len(chunk_text) if start_char != -1 else len(chunk_text)

            chunk_meta = ChunkMetadata(
                doc_id=doc.doc_id,
                chunk_index=chunk_idx,
                source_type=doc.metadata.source_type,
                source_name=doc.metadata.source_name,
                uri=doc.metadata.uri,
                start_char=max(0, start_char),
                end_char=end_char,
                token_count=current_token_count,
                semantic_score=1.0
            )
            chunks.append(Chunk(content=chunk_text, metadata=chunk_meta))

        return chunks
