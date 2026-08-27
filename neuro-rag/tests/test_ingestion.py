"""
Tests for Ingestion Parsers and Semantic Chunker
Author: Mohammad Subhan Pasha
"""

import pytest
from neuro_rag.ingestion.parsers import DocumentParserFactory, URLParser, NotionParser
from neuro_rag.ingestion.semantic_chunker import SemanticChunker
from neuro_rag.ingestion.schemas import Document, DocumentMetadata


def test_notion_parser_raw_text():
    parser = NotionParser()
    doc = parser.parse("Notion raw workspace text content for Pasha Neuro RAG test.")
    assert isinstance(doc, Document)
    assert doc.metadata.source_type == "notion"
    assert "Pasha Neuro RAG" in doc.content


def test_semantic_chunker_basic():
    chunker = SemanticChunker(target_chunk_tokens=50, min_chunk_tokens=20, max_chunk_tokens=100)
    sample_text = (
        "PASHA-NEURO-RAG is a self-correcting enterprise RAG architecture built by Mohammad Subhan Pasha. "
        "It supports PDF, DOCX, URL, and Notion document parsing. "
        "The system utilizes Qdrant vector database and BM25 sparse retrieval with RRF fusion. "
        "Furthermore, Cross-Encoder re-ranking with Cohere or BGE reranker ensures top precision. "
        "The LangGraph self-correcting loop performs critique and query refinement automatically. "
        "Finally, DeBERTa-v3 NLI validator prevents hallucination by checking source entailment."
    )
    doc = Document(
        content=sample_text,
        metadata=DocumentMetadata(source_type="pdf", source_name="test.pdf")
    )

    chunks = chunker.chunk_document(doc)
    assert len(chunks) > 0
    assert all(chunk.content for chunk in chunks)
    assert chunks[0].metadata.doc_id == doc.doc_id
