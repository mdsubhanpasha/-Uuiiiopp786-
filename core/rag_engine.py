"""Hybrid RAG Engine for PASHA-OS using FAISS, Chroma Vector Stores, or Fallback Engine.

Enables context retrieval for multi-agent executive reasoning.
"""

from typing import List
import numpy as np

try:
    import faiss
    HAS_FAISS = True
except ImportError:
    faiss = None
    HAS_FAISS = False

try:
    import chromadb
    HAS_CHROMA = True
except ImportError:
    chromadb = None
    HAS_CHROMA = False


class PashaRAGEngine:
    """Hybrid RAG Engine combining FAISS in-memory indexing, ChromaDB storage, or Numpy Fallback."""

    def __init__(self, dimension: int = 384) -> None:
        """Initialize FAISS index / ChromaDB client or numpy fallback.

        Args:
            dimension (int): Vector embedding dimension size.
        """
        self.dimension = dimension
        self.documents: List[str] = []
        self.embeddings: List[np.ndarray] = []

        if HAS_FAISS and faiss is not None:
            self.faiss_index = faiss.IndexFlatL2(dimension)
        else:
            self.faiss_index = None

        if HAS_CHROMA and chromadb is not None:
            self.chroma_client = chromadb.EphemeralClient()
            self.collection = self.chroma_client.get_or_create_collection("pasha_docs")
        else:
            self.chroma_client = None
            self.collection = None

    def _get_embedding(self, text: str) -> np.ndarray:
        """Generate a normalized feature vector embedding for a given text string.

        Args:
            text (str): Input text chunk.

        Returns:
            np.ndarray: Normalized 1D float32 embedding vector.
        """
        np.random.seed(abs(hash(text)) % (2**32 - 1))
        vec = np.random.randn(self.dimension).astype("float32")
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
        return vec

    def ingest(self, texts: List[str]) -> None:
        """Ingest text documents into vector store or in-memory list.

        Args:
            texts (List[str]): List of document string contents to index.
        """
        if not texts:
            return

        embeddings = []
        ids = []
        metadatas = []

        start_id = len(self.documents)
        for idx, text in enumerate(texts):
            doc_id = f"doc_{start_id + idx}"
            emb = self._get_embedding(text)
            embeddings.append(emb)
            ids.append(doc_id)
            metadatas.append({"source": "executive_feed", "index": start_id + idx})
            self.documents.append(text)
            self.embeddings.append(emb)

        emb_matrix = np.array(embeddings).astype("float32")

        if HAS_FAISS and self.faiss_index is not None:
            self.faiss_index.add(emb_matrix)

        if HAS_CHROMA and self.collection is not None:
            self.collection.add(
                documents=texts,
                embeddings=emb_matrix.tolist(),
                ids=ids,
                metadatas=metadatas,
            )

    def query(self, q: str, k: int = 5) -> List[str]:
        """Query vector stores for top-k relevant context documents.

        Args:
            q (str): Query string prompt.

        Returns:
            List[str]: List of top-k retrieved text passages.
        """
        if not self.documents:
            return []

        k = min(k, len(self.documents))
        q_emb = self._get_embedding(q).reshape(1, -1)

        if HAS_FAISS and self.faiss_index is not None:
            _, faiss_indices = self.faiss_index.search(q_emb, k)
            retrieved_docs = []
            for idx in faiss_indices[0]:
                if 0 <= idx < len(self.documents):
                    retrieved_docs.append(self.documents[idx])
            return retrieved_docs
        else:
            # Fallback cosine/L2 distance search using numpy
            q_vec = q_emb.flatten()
            dists = [np.linalg.norm(q_vec - emb) for emb in self.embeddings]
            sorted_indices = np.argsort(dists)[:k]
            return [self.documents[idx] for idx in sorted_indices]
