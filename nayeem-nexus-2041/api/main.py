"""
FastAPI REST Interface for NAYEEM-NEXUS-2041: The Autonomous Sentient OS.
Endpoints: /ingest/secure, /ask/nexus, /evolve/status, /vault/status, /health
"""

import os
import sys
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Ensure nayeem-nexus-2041 root is in path
NEXUS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if NEXUS_ROOT not in sys.path:
    sys.path.insert(0, NEXUS_ROOT)

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


app = FastAPI(
    title="NAYEEM-NEXUS-2041: The Autonomous Sentient OS API",
    description="Quantum Encrypted, Self-Evolving Black Box Operating System API",
    version="2041.1.0",
)

# Initialize Black-Box Core Subsystems
vault = QuantumVault()
brain = SentientBrain()
self_heal = SelfHealingLoop()
timeline = EvolutionTimeline(current_simulated_year=2041)
extractor = SentientExtractor()
embedder = EncryptedEmbedder()
vector_store = QuantumVectorStore()
llm_router = BrainRouter()
evaluator = EvalEngine()
gitops = GitOpsEngine()


# Pydantic Schemas
class IngestRequest(BaseModel):
    doc_id: str = Field(default="DOC-2041-001", description="Unique Document ID")
    content: str = Field(..., description="Raw text or unstructured document content")
    source_type: str = Field(default="UNSTRUCTURED_DOCUMENT", description="Source content type")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Metadata dictionary")


class QueryRequest(BaseModel):
    query: str = Field(..., description="User prompt or system instruction")
    context: Optional[str] = Field(default=None, description="Optional extra context")
    encrypt_response: bool = Field(default=True, description="Encrypt payload in response")


class YearUpdateRequest(BaseModel):
    target_year: int = Field(..., ge=2026, le=2041, description="Target year between 2026 and 2041")


@app.get("/")
@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Return health status and active OS parameters."""
    return {
        "status": "OPERATIONAL",
        "system": "NAYEEM-NEXUS-2041",
        "singularity_phase": timeline.get_evolution_status()["current_phase"],
        "system_health_score": self_heal.get_self_heal_status()["system_health_score"],
        "quantum_vault_sealed": vault.get_vault_status()["sealed"],
        "timestamp": time.time(),
    }


@app.post("/ingest/secure")
def secure_ingest(payload: IngestRequest) -> Dict[str, Any]:
    """Ingest, redact PII, encrypt embeddings, and store document into quantum vector store."""
    try:
        # Extract context and sanitize
        extracted = extractor.extract_context(
            raw_input=payload.content,
            source_type=payload.source_type,
            metadata=payload.metadata,
        )

        # Generate encrypted embedding
        embed_data = embedder.generate_encrypted_embedding(
            text=extracted["sanitized_text"],
            model_type="NOMIC",
        )

        # Store in Vector Nexus
        storage_res = vector_store.add_document(
            doc_id=payload.doc_id,
            text=extracted["sanitized_text"],
            embedding=embed_data["encrypted_vector"],
            metadata=extracted["metadata"],
        )

        # Encrypt summary payload via Quantum Vault
        encrypted_summary = vault.encrypt_payload({
            "doc_id": payload.doc_id,
            "pii_redacted": extracted["pii_redacted"],
            "domain": extracted["context_domain"],
            "storage": storage_res,
        })

        return {
            "status": "SECURELY_INGESTED",
            "doc_id": payload.doc_id,
            "extraction_info": extracted,
            "embedding_model": embed_data["model"],
            "storage_status": storage_res,
            "obfuscated_encrypted_payload": encrypted_summary,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@app.post("/ask/nexus")
def ask_nexus(payload: QueryRequest) -> Dict[str, Any]:
    """Route query through 11-LLM Battle Router, evaluate quality, auto re-query if hallucination high."""
    try:
        # Step 1: Process query via Sentient Brain MoE Router
        route_res = llm_router.route_query(query=payload.query, context=payload.context)

        # Step 2: Evaluate using Giskard + RAGAS Hallucination Guard
        eval_res = evaluator.evaluate_response(
            query=payload.query,
            response_text=route_res["response"],
            context=payload.context,
            winning_model=route_res["winner_model"],
        )

        # Step 3: Trigger auto re-query if hallucination score exceeded threshold
        if eval_res["requires_requery"]:
            requery_res = evaluator.trigger_auto_requery_if_needed(
                eval_result=eval_res,
                router_fn=llm_router.route_query,
                query=payload.query,
                context=payload.context,
            )
            final_response_text = requery_res.get("new_response", route_res["response"])
            final_winner = requery_res.get("new_winner", route_res["winner_model"])
            final_eval = requery_res.get("final_eval", eval_res)
            requeried = True
        else:
            final_response_text = route_res["response"]
            final_winner = route_res["winner_model"]
            final_eval = eval_res
            requeried = False

        # Step 4: Obfuscate and quantum encrypt response payload
        response_data = {
            "query": payload.query,
            "winner_model": final_winner,
            "response": final_response_text,
            "eval_metrics": final_eval,
            "auto_requeried": requeried,
        }

        encrypted_response = vault.encrypt_payload(response_data) if payload.encrypt_response else None

        return {
            "status": "COMPLETED",
            "winning_model": final_winner,
            "response_text": final_response_text,
            "evaluation": final_eval,
            "auto_requeried": requeried,
            "latency_ms": route_res["latency_ms"],
            "obfuscated_encrypted_response": encrypted_response,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Nexus query execution error: {str(e)}")


@app.get("/evolve/status")
def evolve_status() -> Dict[str, Any]:
    """Get 2026->2041 evolution timeline status and active milestone telemetry."""
    return {
        "status": "ACTIVE",
        "evolution_info": timeline.get_evolution_status(),
        "timeline_milestones": timeline.get_timeline(),
        "brain_status": brain.get_brain_status(),
    }


@app.post("/evolve/year")
def evolve_year(payload: YearUpdateRequest) -> Dict[str, Any]:
    """Simulate active operating year shift in the evolution engine."""
    res = timeline.set_active_year(payload.target_year)
    return res


@app.get("/vault/status")
def vault_status() -> Dict[str, Any]:
    """Get quantum vault status, rotation logs, anti-tamper telemetry, and seal state."""
    return {
        "vault_telemetry": vault.get_vault_status(),
        "anti_tamper": vault.verify_anti_tamper(),
    }


@app.post("/vault/rotate")
def vault_rotate() -> Dict[str, Any]:
    """Rotate quantum vault key lattice."""
    return vault.rotate_keys()


@app.get("/self-heal/status")
def self_heal_status() -> Dict[str, Any]:
    """Get self-healing pipeline loops health metrics."""
    return self_heal.get_self_heal_status()


@app.post("/self-heal/repair")
def self_heal_repair() -> Dict[str, Any]:
    """Trigger automated system repair loops."""
    return self_heal.trigger_auto_repair()


@app.get("/gitops/status")
def gitops_status() -> Dict[str, Any]:
    """Get GitOps drift detection status across Helm, Kustomize, OPA, Kyverno, ArgoCD, Flux, and Vault ESO."""
    return gitops.get_gitops_status()


@app.post("/gitops/remediate")
def gitops_remediate() -> Dict[str, Any]:
    """Trigger GitOps auto-remediation sync back to SSOT."""
    return gitops.auto_remediate_drift()
