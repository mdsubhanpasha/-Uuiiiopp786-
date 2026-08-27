"""
Tests for FastAPI API Endpoints & Metrics
Author: Mohammad Subhan Pasha
"""

import pytest
from fastapi.testclient import TestClient
from neuro_rag.api.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["author"] == "Mohammad Subhan Pasha"


def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "neuro_rag_requests_total" in response.text or "python_info" in response.text


def test_chat_non_streaming():
    response = client.post(
        "/chat",
        json={"query": "What is PASHA-NEURO-RAG?", "stream": False}
    )
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "groundedness_score" in data
    assert "citations" in data
    assert data["author"] == "Mohammad Subhan Pasha"


def test_ingest_raw_text():
    response = client.post(
        "/ingest",
        data={"raw_text": "Mohammad Subhan Pasha created the PASHA-NEURO-RAG enterprise RAG solution.", "source_type": "notion"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["chunk_count"] > 0
