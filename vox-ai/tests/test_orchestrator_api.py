"""Unit tests for Voice Pipeline Orchestrator & FastAPI endpoints."""

import asyncio
import os
import sys
import tempfile
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import init_db, seed_db  # noqa: E402
from main import app  # noqa: E402
from orchestrator import VoicePipelineOrchestrator  # noqa: E402


@pytest.fixture
def client_with_db():
    """Fixture providing TestClient with seeded temporary DB."""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    init_db(path)
    seed_db(path, num_orders=50)

    client = TestClient(app)
    yield client
    if os.path.exists(path):
        os.remove(path)


def test_health_check_endpoint(client_with_db):
    """Tests GET /api/health returns 200 OK."""
    response = client_with_db.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["target_latency_ms"] == 1200.0


def test_get_order_endpoint(client_with_db):
    """Tests GET /api/orders/ORD-1001 endpoint."""
    response = client_with_db.get("/api/orders/ORD-1001")
    assert response.status_code == 200
    data = response.json()
    assert data["found"] is True
    assert data["order_id"] == "ORD-1001"


def test_create_appointment_endpoint(client_with_db):
    """Tests POST /api/appointments endpoint."""
    payload = {
        "customer_name": "Test User",
        "date": "2026-03-30",
        "time_slot": "10:00 AM",
        "service_type": "Consultation"
    }
    response = client_with_db.post("/api/appointments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["status"] == "Confirmed"


def test_orchestrator_turn_and_interrupt():
    """Tests orchestrator turn processing and mid-speech interrupt."""
    async def run():
        orchestrator = VoicePipelineOrchestrator(session_id="test_session")

        events = []
        async for event in orchestrator.process_user_audio_chunk(b"Hello check order ORD-1001"):
            events.append(event)

        assert len(events) > 0
        event_types = [e.get("event") for e in events]
        assert "stt_complete" in event_types
        assert "llm_complete" in event_types
        assert "turn_complete" in event_types

        # Test interrupt signal
        interrupt_res = orchestrator.trigger_interrupt()
        assert interrupt_res["status"] == "interrupted"
        assert orchestrator.is_interrupted is True

    asyncio.run(run())
