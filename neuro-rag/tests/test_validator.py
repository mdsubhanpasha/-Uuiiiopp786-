"""
Tests for NLI Validator Agent (Hallucination Guard)
Author: Mohammad Subhan Pasha
"""

import pytest
from neuro_rag.ingestion.schemas import Chunk, ChunkMetadata
from neuro_rag.validation.validator import ValidatorAgent


def test_validator_grounded_answer():
    chunks = [
        Chunk(
            content="Mohammad Subhan Pasha is the principal architect of PASHA-NEURO-RAG enterprise platform.",
            metadata=ChunkMetadata(doc_id="d1", chunk_index=0, source_type="text", source_name="spec.txt")
        )
    ]

    agent = ValidatorAgent(threshold=0.50)
    grounded_answer = "Mohammad Subhan Pasha created the PASHA-NEURO-RAG platform."

    result = agent.validate_answer(grounded_answer, chunks)
    assert result.is_grounded is True
    assert result.final_answer == grounded_answer
    assert result.groundedness_score >= 0.50


def test_validator_hallucinated_answer():
    chunks = [
        Chunk(
            content="Mohammad Subhan Pasha is the principal architect of PASHA-NEURO-RAG enterprise platform.",
            metadata=ChunkMetadata(doc_id="d1", chunk_index=0, source_type="text", source_name="spec.txt")
        )
    ]

    agent = ValidatorAgent(threshold=0.75)
    hallucinated_answer = "The Eiffel Tower is located in Tokyo, Japan, and was constructed in 1999."

    result = agent.validate_answer(hallucinated_answer, chunks)
    assert result.is_grounded is False
    assert result.final_answer == "I don't have enough info in documents"
    assert result.rejection_reason is not None
