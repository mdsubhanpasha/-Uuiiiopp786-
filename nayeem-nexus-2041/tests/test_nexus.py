"""
Comprehensive Unit & Integration Test Suite for NAYEEM-NEXUS-2041: The Autonomous Sentient OS.
"""

import importlib.util
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure nayeem-nexus-2041 directory is added to sys.path
NEXUS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if NEXUS_DIR not in sys.path:
    sys.path.insert(0, NEXUS_DIR)

from nexus_core.quantum_vault import QuantumVault  # noqa: E402
from nexus_core.sentient_brain import SentientBrain  # noqa: E402
from nexus_core.self_heal import SelfHealingLoop  # noqa: E402
from nexus_core.evolution_timeline import EvolutionTimeline  # noqa: E402
from ingestion_layer.sentient_extractor import SentientExtractor  # noqa: E402
from ingestion_layer.encrypted_embedder import EncryptedEmbedder  # noqa: E402
from vector_nexus.quantum_vector_store import QuantumVectorStore  # noqa: E402
from llm_nexus.brain_router import BrainRouter  # noqa: E402
from eval_nexus.eval_engine import EvalEngine  # noqa: E402
from gitops_nexus.gitops_engine import GitOpsEngine  # noqa: E402


# Load FastAPI app dynamically to avoid top-level api namespace collision
spec = importlib.util.spec_from_file_location("nexus_api_main", os.path.join(NEXUS_DIR, "api", "main.py"))
api_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(api_module)
client = TestClient(api_module.app)


def test_quantum_vault():
    vault = QuantumVault()
    status = vault.get_vault_status()
    assert status["algorithm"] == "AES-2048Q-LATTICE"
    assert status["sealed"] is False

    payload = {"secret": "quantum_data_2041", "level": 5}
    encrypted = vault.encrypt_payload(payload)
    assert encrypted.startswith("Q2048V1:")

    decrypted = vault.decrypt_payload(encrypted)
    assert decrypted["secret"] == "quantum_data_2041"

    # Key Rotation
    rot_res = vault.rotate_keys()
    assert rot_res["key_version"] == 2

    # Seal and Unseal
    vault.seal_vault()
    assert vault.get_vault_status()["sealed"] is True

    with pytest.raises(PermissionError):
        vault.encrypt_payload("forbidden")

    vault.unseal_vault("NEXUS-2041-UNSEAL-KEY")
    assert vault.get_vault_status()["sealed"] is False


def test_sentient_brain():
    brain = SentientBrain()
    status = brain.get_brain_status()
    assert status["connected_llm_nodes"] == 11
    assert "Phi-4" in status["models"]

    res = brain.process_holographic_query("Explain neural quantum lattice.")
    assert "NEXUS-2041 SENTIENT BRAIN RESPONSE" in res["response"]
    assert res["winning_model"] in status["models"]

    rewire_res = brain.rewire_synapses({"Phi-4": 0.5})
    assert rewire_res["status"] == "REWIRED"


def test_self_healing_loop():
    heal = SelfHealingLoop()
    status = heal.get_self_heal_status()
    assert status["system_health_score"] == 100.0

    faults = heal.detect_faults({"vault": {"tamper_attempts": 2}})
    assert len(faults) == 1
    assert heal.get_self_heal_status()["system_health_score"] < 100.0

    repair_res = heal.trigger_auto_repair()
    assert repair_res["status"] == "REPAIRED"
    assert heal.get_self_heal_status()["system_health_score"] == 100.0


def test_evolution_timeline():
    timeline = EvolutionTimeline(2041)
    status = timeline.get_evolution_status()
    assert status["current_year"] == 2041
    assert status["singularity_reached"] is True

    timeline_list = timeline.get_timeline()
    assert len(timeline_list) == 5

    res_shift = timeline.set_active_year(2029)
    assert res_shift["active_year"] == 2029


def test_sentient_extractor():
    extractor = SentientExtractor()
    text = "Contact CEO at user@domain.com or call 555-019-2834 with sk-abcdef123456789012345678."
    extracted = extractor.extract_context(text)

    assert extracted["pii_redacted"] is True
    assert "[REDACTED_EMAIL]" in extracted["sanitized_text"]
    assert "[REDACTED_SECRET_KEY]" in extracted["sanitized_text"]


def test_encrypted_embedder():
    embedder = EncryptedEmbedder("NOMIC")
    emb = embedder.generate_encrypted_embedding("Quantum OS Test Payload")

    assert emb["model"] == "NOMIC"
    assert len(emb["encrypted_vector"]) == 768
    assert emb["quantum_encrypted"] is True

    decrypted_vec = embedder.verify_and_decrypt_vector(emb)
    assert len(decrypted_vec) == 768


def test_quantum_vector_store():
    store = QuantumVectorStore("Qdrant")
    store.add_document("DOC1", "Quantum vector store doc", [0.1, 0.2, 0.3, 0.4])

    results = store.similarity_search([0.1, 0.2, 0.3, 0.4], top_k=1)
    assert len(results) == 1
    assert results[0]["doc_id"] == "DOC1"

    rot = store.rotate_vector_keys()
    assert rot["status"] == "VECTOR_KEYS_ROTATED"


def test_brain_router():
    router = BrainRouter()
    status = router.get_router_status()
    assert status["total_models"] == 11

    route_res = router.route_query("Analyze quantum security protocol")
    assert route_res["winner_model"] in status["supported_models"]
    assert "latency_ms" in route_res


def test_eval_engine():
    evaluator = EvalEngine()
    res = evaluator.evaluate_response("What is Nexus?", "Nexus is the autonomous sentient OS", winning_model="Phi-4")

    assert "faithfulness" in res
    assert "hallucination_score" in res

    eval_status = evaluator.get_eval_status()
    assert eval_status["evaluations_conducted"] == 1


def test_gitops_engine():
    gitops = GitOpsEngine()
    status = gitops.get_gitops_status()
    assert "Helm" in status["tools_integrated"]
    assert status["in_sync"] is True

    drift = gitops.detect_drift({"nexus-opa-policy": "Unauthorized mutation"})
    assert len(drift) == 1
    assert gitops.get_gitops_status()["in_sync"] is False

    rem = gitops.auto_remediate_drift()
    assert rem["status"] == "REMEDIATED"
    assert gitops.get_gitops_status()["in_sync"] is True


def test_fastapi_endpoints():
    # Test Health
    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json()["system"] == "NAYEEM-NEXUS-2041"

    # Test Ingest
    ingest_req = {
        "doc_id": "TEST-DOC-1",
        "content": "Secret payload with email admin@nexus2041.org",
        "source_type": "TEXT",
    }
    i_res = client.post("/ingest/secure", json=ingest_req)
    assert i_res.status_code == 200
    assert i_res.json()["status"] == "SECURELY_INGESTED"

    # Test Query
    q_res = client.post("/ask/nexus", json={"query": "Who created NAYEEM-NEXUS-2041?"})
    assert q_res.status_code == 200
    assert q_res.json()["status"] == "COMPLETED"

    # Test Vault Status
    v_res = client.get("/vault/status")
    assert v_res.status_code == 200
    assert "vault_telemetry" in v_res.json()

    # Test Evolution Status
    e_res = client.get("/evolve/status")
    assert e_res.status_code == 200
    assert e_res.json()["evolution_info"]["current_year"] == 2041
