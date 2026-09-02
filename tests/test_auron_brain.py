"""Unit and Integration Tests for AURON-4000 Quantum Governance Plane."""

from fastapi.testclient import TestClient

from api.main import app
from core.orchestration.auron_brain import AuronBrain

client = TestClient(app)


def test_auron_brain_agent_registry():
    """Test that AuronBrain initializes exactly 4,000 agents across departments."""
    brain = AuronBrain()
    assert len(brain.agents) == 4000
    assert sum(brain.DEPARTMENTS.values()) == 4000

    # Check unique Agent IDs
    agent_ids = {a["agent_id"] for a in brain.agents}
    assert len(agent_ids) == 4000
    assert "AGT-0001" in agent_ids
    assert "AGT-4000" in agent_ids


def test_quantum_circuit_construction():
    """Test 64-qubit Qiskit quantum circuit layout and gate composition."""
    brain = AuronBrain()
    qc = brain.build_quantum_circuit()

    assert qc.num_qubits == 64
    assert qc.num_clbits == 64
    assert qc.depth() > 0

    ops = qc.count_ops()
    assert ops.get("h") == 64
    assert ops.get("cx") >= 63
    assert ops.get("rz") == 64
    assert ops.get("measure") == 64


def test_quantum_circuit_simulation():
    """Test Qiskit 64-qubit Zero-Trust simulation telemetry."""
    brain = AuronBrain()
    telemetry = brain.run_quantum_circuit_simulation()

    assert telemetry["status"] == "SUCCESS"
    assert telemetry["num_qubits"] == 64
    assert telemetry["fidelity_score"] >= 0.99
    assert telemetry["quantum_zero_trust_token"].startswith("QZT-")
    assert telemetry["verification_status"] == "VERIFIED_ZERO_TRUST"
    assert telemetry["confidential_enclave_attested"] is True
    assert "identity_qubits" in telemetry["registers"]


def test_governance_status():
    """Test governance status aggregation for 4,000 agents."""
    brain = AuronBrain()
    status = brain.get_governance_status()

    assert status["system_name"] == "AURON-4000 Quantum Governance Plane"
    assert status["status"] == "HEALTHY"
    assert status["total_agents"] == 4000
    assert status["active_agents"] == 4000
    assert status["quantum_verification_rate_percent"] == 100.0
    assert status["confidential_enclaves_active"] == 4000
    assert len(status["department_breakdown"]) == len(brain.DEPARTMENTS)


def test_verify_agent_policy():
    """Test quantum policy claim verification for specific agent."""
    brain = AuronBrain()
    proof = brain.verify_agent_policy(
        "AGT-0001", "Confidential cloud treasury execution"
    )

    assert proof["status"] == "SUCCESS"
    assert proof["agent_id"] == "AGT-0001"
    assert proof["verified"] is True
    assert proof["quantum_proof_hash"].startswith("QPROOF-")
    assert proof["quantum_token"].startswith("QZT-")

    # Test invalid agent ID
    invalid_proof = brain.verify_agent_policy("AGT-9999", "Invalid policy")
    assert invalid_proof["status"] == "ERROR"


def test_get_agents_pagination_and_filter():
    """Test agent search and pagination."""
    brain = AuronBrain()

    # Test pagination
    page1 = brain.get_agents(page=1, limit=50)
    assert len(page1["agents"]) == 50
    assert page1["total"] == 4000
    assert page1["total_pages"] == 80

    # Test department filter
    dept_name = "Cyber Defense & Zero-Trust"
    dept_filtered = brain.get_agents(department=dept_name, limit=1000)
    assert dept_filtered["total"] == 500

    # Test search filter
    search_res = brain.get_agents(search="AGT-0042")
    assert search_res["total"] >= 1
    assert search_res["agents"][0]["agent_id"] == "AGT-0042"


def test_api_health_endpoint():
    """Test FastAPI /health REST endpoint."""
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert "auron-4000" in data["service"]
    assert data["agents_active"] == 4000
    assert data["quantum_engine_status"] == "ONLINE"


def test_api_quantum_circuit_endpoint():
    """Test FastAPI /quantum/circuit REST endpoint."""
    resp = client.get("/quantum/circuit")
    assert resp.status_code == 200
    data = resp.json()
    assert data["num_qubits"] == 64
    assert data["status"] == "SUCCESS"
    assert "quantum_zero_trust_token" in data


def test_api_quantum_governance_status_endpoint():
    """Test FastAPI /quantum/governance/status REST endpoint."""
    resp = client.get("/quantum/governance/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_agents"] == 4000
    assert data["system_name"] == "AURON-4000 Quantum Governance Plane"


def test_api_quantum_policy_verify_endpoint():
    """Test FastAPI /quantum/policy/verify REST endpoint."""
    resp = client.post(
        "/quantum/policy/verify",
        json={
            "agent_id": "AGT-0001",
            "policy_claim": "Approved enclave operation",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "SUCCESS"
    assert data["verified"] is True


def test_api_list_agents_endpoint():
    """Test FastAPI /agents REST endpoint."""
    resp = client.get("/agents?limit=10")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["agents"]) == 10
    assert data["total"] == 4000
