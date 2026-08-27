"""
Tests for Hybrid Search and Qdrant / BM25 Indexing Engine
Author: Mohammad Subhan Pasha
"""

import pytest
from neuro_rag.ingestion.schemas import Chunk, ChunkMetadata
from neuro_rag.retrieval.vector_store import VectorStoreManager
from neuro_rag.retrieval.bm25_retriever import BM25Retriever
from neuro_rag.retrieval.reranker import CrossEncoderReranker
from neuro_rag.retrieval.hybrid_search import HybridSearchEngine


@pytest.fixture
def sample_chunks():
    chunks = [
        Chunk(
            content="Mohammad Subhan Pasha is the creator of PASHA-NEURO-RAG.",
            metadata=ChunkMetadata(doc_id="doc1", chunk_index=0, source_type="text", source_name="author.txt")
        ),
        Chunk(
            content="Qdrant is a high performance vector database used for dense neural embeddings.",
            metadata=ChunkMetadata(doc_id="doc2", chunk_index=0, source_type="text", source_name="qdrant.txt")
        ),
        Chunk(
            content="Hybrid search combines BM25 keyword matching and dense vector search via Reciprocal Rank Fusion.",
            metadata=ChunkMetadata(doc_id="doc3", chunk_index=0, source_type="text", source_name="hybrid.txt")
        )
    ]
    return chunks


def test_vector_store_in_memory(sample_chunks):
    vstore = VectorStoreManager(in_memory=True)
    count = vstore.index_chunks(sample_chunks)
    assert count == 3

    results = vstore.search("Mohammad Subhan Pasha", top_k=3)
    assert len(results) > 0
    assert any(c.content != "" for c in results)


def test_bm25_retriever(sample_chunks):
    bm25 = BM25Retriever()
    bm25.index_chunks(sample_chunks)

    results = bm25.search("Qdrant database", top_k=2)
    assert len(results) > 0
    assert "Qdrant" in results[0].content


def test_hybrid_search_engine(sample_chunks):
    vstore = VectorStoreManager(in_memory=True)
    vstore.index_chunks(sample_chunks)

    bm25 = BM25Retriever()
    bm25.index_chunks(sample_chunks)

    engine = HybridSearchEngine(vector_store=vstore, bm25_retriever=bm25)
    final_results = engine.hybrid_search("Tell me about hybrid search and Reciprocal Rank Fusion", top_k_retrieval=3, top_k_rerank=2)

    assert len(final_results) <= 2
    assert any("Hybrid search" in r.content for r in final_results)
