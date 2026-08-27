"""
PASHA-NEURO-RAG Qdrant Vector Store Management
Author: Mohammad Subhan Pasha
"""

import os
import logging
from typing import List, Dict, Any, Optional
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest

from neuro_rag.config import settings
from neuro_rag.ingestion.schemas import Chunk, ChunkMetadata

logger = logging.getLogger(__name__)


class VectorStoreManager:
    """
    Manages Qdrant vector database operations including collection creation,
    dense vector indexing, and similarity search with metadata filtering.
    """

    def __init__(self, in_memory: bool = False):
        self.collection_name = settings.QDRANT_COLLECTION_NAME
        self.vector_size = settings.VECTOR_SIZE

        if in_memory:
            self.client = QdrantClient(":memory:")
        else:
            try:
                self.client = QdrantClient(
                    url=settings.QDRANT_URL,
                    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                    timeout=5.0
                )
                # Test connection
                self.client.get_collections()
            except Exception as e:
                logger.warning(f"Could not connect to Qdrant at {settings.QDRANT_URL}. Falling back to in-memory mode: {e}")
                self.client = QdrantClient(":memory:")

        self._ensure_collection()

    def _ensure_collection(self):
        try:
            collections = self.client.get_collections().collections
            exists = any(c.name == self.collection_name for c in collections)
            if not exists:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=rest.VectorParams(
                        size=self.vector_size,
                        distance=rest.Distance.COSINE
                    )
                )
                logger.info(f"Created Qdrant collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error checking/creating Qdrant collection: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding via OpenAI API if key available, else synthetic deterministic vector for testing.
        """
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-placeholder"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                resp = client.embeddings.create(
                    input=text,
                    model=settings.EMBEDDING_MODEL
                )
                return resp.data[0].embedding
            except Exception as e:
                logger.warning(f"OpenAI embedding call failed: {e}. Using fallback vector embedding.")

        # Fallback pseudo-embedding based on hash for unit testing without API keys
        rng = np.random.RandomState(seed=abs(hash(text)) % (2**32))
        vec = rng.randn(self.vector_size).astype(float)
        vec /= np.linalg.norm(vec)
        return vec.tolist()

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-placeholder"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                resp = client.embeddings.create(
                    input=texts,
                    model=settings.EMBEDDING_MODEL
                )
                return [d.embedding for d in resp.data]
            except Exception as e:
                logger.warning(f"Batch OpenAI embedding failed: {e}. Using fallback vector embeddings.")

        return [self.generate_embedding(t) for t in texts]

    def index_chunks(self, chunks: List[Chunk]) -> int:
        if not chunks:
            return 0

        texts = [c.content for c in chunks]
        embeddings = self.generate_embeddings_batch(texts)

        points = []
        for i, chunk in enumerate(chunks):
            chunk.embedding = embeddings[i]
            points.append(
                rest.PointStruct(
                    id=chunk.chunk_id,
                    vector=embeddings[i],
                    payload={
                        "chunk_id": chunk.chunk_id,
                        "content": chunk.content,
                        "doc_id": chunk.metadata.doc_id,
                        "chunk_index": chunk.metadata.chunk_index,
                        "source_type": chunk.metadata.source_type,
                        "source_name": chunk.metadata.source_name,
                        "uri": chunk.metadata.uri,
                        "token_count": chunk.metadata.token_count,
                    }
                )
            )

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return len(points)

    def search(self, query: str, top_k: int = 10) -> List[Chunk]:
        query_vec = self.generate_embedding(query)

        if hasattr(self.client, "query_points"):
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_vec,
                limit=top_k
            ).points
        else:
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vec,
                limit=top_k
            )

        chunks = []
        for hit in search_results:
            p = hit.payload
            meta = ChunkMetadata(
                doc_id=p.get("doc_id", ""),
                chunk_index=p.get("chunk_index", 0),
                source_type=p.get("source_type", "unknown"),
                source_name=p.get("source_name", "unknown"),
                uri=p.get("uri"),
                token_count=p.get("token_count", 0),
                semantic_score=hit.score
            )
            chunk = Chunk(
                chunk_id=p.get("chunk_id", str(hit.id)),
                content=p.get("content", ""),
                metadata=meta,
                embedding=None
            )
            chunks.append(chunk)

        return chunks
