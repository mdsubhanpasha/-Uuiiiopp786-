import json
import base64
import pytest
from fastapi.testclient import TestClient
from main import app, ENCRYPTED_AUDIT_LOGS

client = TestClient(app)

def setup_function():
    ENCRYPTED_AUDIT_LOGS.clear()

def test_healthz():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_metrics():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert b"remediator_actions_total" in response.content

def test_successful_remediation():
    payload = {
        "event_id": "evt-suspicious-01",
        "namespace": "prod",
        "rollout_name": "payment-api",
        "anomaly_score": 0.92,
        "threat_category": "reverse_shell"
    }
    response = client.post("/remediate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "EXECUTED"
    assert data["enclave_verified"] is True
    assert data["opa_approved"] is True
    assert len(data["encrypted_log_hash"]) == 64
    assert len(ENCRYPTED_AUDIT_LOGS) == 1

def test_opa_denied_low_anomaly_score():
    payload = {
        "event_id": "evt-normal-01",
        "namespace": "prod",
        "rollout_name": "payment-api",
        "anomaly_score": 0.15,
        "threat_category": "normal_exec",
        "opa_policy_override": False
    }
    response = client.post("/remediate", json=payload)
    assert response.status_code == 422
    assert "denied by OPA security policy" in response.json()["detail"]

def test_enclave_attestation_failure():
    invalid_attestation = base64.b64encode(json.dumps({"invalid": "doc"}).encode('utf-8')).decode('utf-8')
    payload = {
        "event_id": "evt-suspicious-02",
        "namespace": "prod",
        "rollout_name": "payment-api",
        "anomaly_score": 0.95,
        "threat_category": "reverse_shell",
        "enclave_attestation_doc": invalid_attestation
    }
    response = client.post("/remediate", json=payload)
    assert response.status_code == 403
    assert "Nitro Enclave attestation failed" in response.json()["detail"]
