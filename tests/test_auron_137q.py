"""
Unit tests for AURON-CORP-137Q
Verifies 137 Agents Registry, Qiskit QAOA Quantum Core, FastAPI REST API, and WebSocket server.
"""

import pytest
from fastapi.testclient import TestClient
from agents.registry import agent_registry, DEPARTMENTS
from brain.quantum_brain import quantum_brain
from main import app

client = TestClient(app)

def test_agents_registry_count_and_departments():
    """Verify registry contains exactly 137 agents distributed across 7 departments."""
    assert agent_registry.count() == 137, f"Expected 137 agents, got {agent_registry.count()}"

    all_agents = agent_registry.list_all()
    departments_found = set(a["department"] for a in all_agents)

    for dept in DEPARTMENTS:
        assert dept in departments_found, f"Department '{dept}' missing from agent registry"
        dept_agents = agent_registry.get_by_department(dept)
        assert len(dept_agents) > 0, f"No agents found for department '{dept}'"

def test_agent_execution():
    """Test individual agent execution logic."""
    sales_agent = agent_registry.get_by_department("Sales")[0]
    result = sales_agent.run("Find 10 high-intent enterprise accounts in Berlin")

    assert result["execution_status"] == "COMPLETED"
    assert result["agent_name"] == sales_agent.name
    assert "Berlin" in result["task"] or "Find" in result["task"]
    assert result["metadata"]["quantum_enhanced"] is True

def test_quantum_qaoa_brain():
    """Test Qiskit 6-qubit QAOA task allocation algorithm."""
    result = quantum_brain.run_qaoa_optimization(num_qubits=6)
    assert result["qubits"] == 6
    assert "QAOA" in result["algorithm"]
    assert "optimal_bitstring" in result
    assert "workload_distribution" in result
    assert len(result["optimal_bitstring"]) == 6

def test_fastapi_health_and_status():
    """Test FastAPI REST endpoints."""
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200
    health_data = health_resp.json()
    assert health_data["status"] == "ONLINE"
    assert health_data["total_agents"] == 137

    status_resp = client.get("/api/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["total_agents"] == 137
    assert len(status_data["agents"]) == 137
    assert len(status_data["departments"]) == 7

def test_fastapi_agent_run_endpoint():
    """Test running specific agent via REST endpoint."""
    resp = client.get("/agents/icp_definer/run?task=Define ICP for Series B FinTechs")
    assert resp.status_code == 200
    data = resp.json()
    assert data["execution_status"] == "COMPLETED"
    assert data["department"] == "Sales"

def test_fastapi_quantum_optimize_endpoint():
    """Test quantum optimize REST endpoint."""
    resp = client.get("/quantum/optimize?qubits=6")
    assert resp.status_code == 200
    data = resp.json()
    assert data["system"] == "AURON-4000 Quantum Core"
    assert data["quantum_brain_result"]["qubits"] == 6

def test_vox_ai_voice_websocket():
    """Test VOX-AI V4 WebSocket voice control endpoint."""
    with client.websocket_connect("/ws/voice") as websocket:
        conn_msg = websocket.receive_json()
        assert conn_msg["type"] == "connection_established"
        assert conn_msg["system"] == "AURON-CORP-137Q"

        # Send voice command
        websocket.send_text("Sales team, find 10 leads in Hamburg")
        voice_resp = websocket.receive_json()
        assert voice_resp["type"] == "voice_response"
        assert "Hamburg" in voice_resp["transcript"]
        assert voice_resp["agent_executed"] is not None
