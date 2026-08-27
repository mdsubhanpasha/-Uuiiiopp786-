"""
Tests for LangGraph Self-Correcting RAG State Graph
Author: Mohammad Subhan Pasha
"""

import pytest
from neuro_rag.ingestion.schemas import Chunk, ChunkMetadata
from neuro_rag.retrieval.vector_store import VectorStoreManager
from neuro_rag.retrieval.bm25_retriever import BM25Retriever
from neuro_rag.retrieval.hybrid_search import HybridSearchEngine
from neuro_rag.orchestration.graph import SelfCorrectingRAGGraph


@pytest.fixture
def rag_engine():
    chunks = [
        Chunk(
            content="PASHA-NEURO-RAG features self-correcting RAG state graph with LangGraph orchestration.",
            metadata=ChunkMetadata(doc_id="d1", chunk_index=0, source_type="text", source_name="architecture.txt")
        ),
        Chunk(
            content="Mohammad Subhan Pasha designed the hybrid BM25 and Qdrant retrieval pipeline.",
            metadata=ChunkMetadata(doc_id="d2", chunk_index=0, source_type="text", source_name="author.txt")
        )
    ]
    vstore = VectorStoreManager(in_memory=True)
    vstore.index_chunks(chunks)
    bm25 = BM25Retriever()
    bm25.index_chunks(chunks)

    search_engine = HybridSearchEngine(vector_store=vstore, bm25_retriever=bm25)
    return search_engine


def test_self_correcting_rag_graph_execution(rag_engine):
    graph_runner = SelfCorrectingRAGGraph(search_engine=rag_engine)
    result = graph_runner.run("Tell me about PASHA-NEURO-RAG architecture and Mohammad Subhan Pasha")

    assert result["original_query"] == "Tell me about PASHA-NEURO-RAG architecture and Mohammad Subhan Pasha"
    assert len(result["retrieved_chunks"]) > 0
    assert result["candidate_answer"] != ""
    assert result["final_answer"] != ""
    assert len(result["citations"]) > 0
    assert "critique_score" in result
    assert "groundedness_score" in result
