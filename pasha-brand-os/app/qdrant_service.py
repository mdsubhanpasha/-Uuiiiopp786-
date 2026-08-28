import os
import uuid
from typing import List, Dict, Any, Optional
import numpy as np
import pandas as pd
from loguru import logger

# Try importing Qdrant and OpenAI clients
try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import Distance, VectorParams, PointStruct
    QDRANT_AVAILABLE = True
except ImportError:
    QDRANT_AVAILABLE = False
    logger.warning("qdrant-client not installed.")

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("openai not installed.")

COLLECTION_NAME = "user_style"
VECTOR_SIZE = 1536  # Default for OpenAI text-embedding-3-small

class QdrantStyleService:
    def __init__(self, qdrant_url: Optional[str] = None):
        self.qdrant_url = qdrant_url or os.getenv("QDRANT_URL", "http://localhost:6333")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")

        self.openai_client = None
        if OPENAI_AVAILABLE and self.openai_api_key and not self.openai_api_key.startswith("sk-placeholder"):
            try:
                self.openai_client = OpenAI(api_key=self.openai_api_key)
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")

        self.client = None
        if QDRANT_AVAILABLE:
            try:
                if self.qdrant_url.startswith("http"):
                    self.client = QdrantClient(url=self.qdrant_url, timeout=5.0)
                else:
                    self.client = QdrantClient(path=":memory:")
                self._ensure_collection()
            except Exception as e:
                logger.warning(f"Qdrant connection failed ({e}). Falling back to in-memory/mock mode.")
                try:
                    self.client = QdrantClient(location=":memory:")
                    self._ensure_collection()
                except Exception as inner_e:
                    logger.error(f"Failed to initialize in-memory Qdrant: {inner_e}")
                    self.client = None

        # Local cache fallback if Qdrant/OpenAI unavailable
        self.local_vectors: List[Dict[str, Any]] = []

    def _ensure_collection(self):
        if not self.client:
            return
        try:
            collections = [c.name for c in self.client.get_collections().collections]
            if COLLECTION_NAME not in collections:
                self.client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE),
                )
                logger.info(f"Created Qdrant collection: {COLLECTION_NAME}")
        except Exception as e:
            logger.warning(f"Error checking/creating collection: {e}")

    def generate_embedding(self, text: str) -> List[float]:
        """Generates embedding using OpenAI text-embedding-3-small, or deterministic pseudo-embedding as fallback."""
        if self.openai_client:
            try:
                res = self.openai_client.embeddings.create(
                    input=text,
                    model="text-embedding-3-small"
                )
                return res.data[0].embedding
            except Exception as e:
                logger.warning(f"OpenAI embedding call failed ({e}). Using deterministic fallback vector.")

        # Deterministic vector based on hash for testing / key-less mode
        np.random.seed(abs(hash(text)) % (2**32))
        vec = np.random.normal(0, 1, VECTOR_SIZE)
        norm = np.linalg.norm(vec)
        return (vec / norm).tolist()

    def ingest_posts_csv(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Ingests CSV of user's past LinkedIn posts.
        Expected columns: post_text, likes, views
        """
        required_cols = {"post_text"}
        if not required_cols.issubset(df.columns):
            raise ValueError(f"CSV must contain at least column: {required_cols}")

        points = []
        ingested_count = 0

        for idx, row in df.iterrows():
            post_text = str(row["post_text"]).strip()
            if not post_text:
                continue

            likes = int(row.get("likes", 0)) if pd.notnull(row.get("likes")) else 0
            views = int(row.get("views", 0)) if pd.notnull(row.get("views")) else 0

            vector = self.generate_embedding(post_text)
            point_id = str(uuid.uuid4())
            payload = {
                "post_text": post_text,
                "likes": likes,
                "views": views,
                "length": len(post_text)
            }

            if self.client:
                points.append(PointStruct(id=point_id, vector=vector, payload=payload))

            self.local_vectors.append({
                "id": point_id,
                "vector": vector,
                "payload": payload
            })
            ingested_count += 1

        if self.client and points:
            try:
                self.client.upsert(collection_name=COLLECTION_NAME, points=points)
                logger.info(f"Upserted {len(points)} points to Qdrant collection '{COLLECTION_NAME}'.")
            except Exception as e:
                logger.error(f"Failed to upsert to Qdrant: {e}")

        return {
            "status": "success",
            "count": ingested_count,
            "collection": COLLECTION_NAME
        }

    def search_similar_style(self, query_text: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Finds top similar past posts to match writing style."""
        query_vector = self.generate_embedding(query_text)

        if self.client:
            try:
                results = self.client.search(
                    collection_name=COLLECTION_NAME,
                    query_vector=query_vector,
                    limit=limit
                )
                if results:
                    return [
                        {
                            "score": res.score,
                            "post_text": res.payload.get("post_text", ""),
                            "likes": res.payload.get("likes", 0),
                            "views": res.payload.get("views", 0)
                        }
                        for res in results
                    ]
            except Exception as e:
                logger.warning(f"Qdrant search error ({e}). Using local fallback search.")

        # Local Cosine Similarity Fallback
        if not self.local_vectors:
            return []

        def cosine_sim(v1, v2):
            return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9))

        scored = [
            (cosine_sim(query_vector, item["vector"]), item["payload"])
            for item in self.local_vectors
        ]
        scored.sort(key=lambda x: x[0], reverse=True)
        top_k = scored[:limit]

        return [
            {
                "score": score,
                "post_text": payload.get("post_text", ""),
                "likes": payload.get("likes", 0),
                "views": payload.get("views", 0)
            }
            for score, payload in top_k
        ]
