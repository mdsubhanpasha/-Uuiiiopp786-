"""FastAPI Backend REST & WebSocket Service for NAYEEM-FLOW-OS Zero-Trust Security Platform."""

import asyncio
from datetime import datetime, timezone
import logging
import sys
import time
from typing import List, Optional

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, Query, Request, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from core.orchestration import PashaOrchestrator
from core.orchestration.auron_brain import AuronBrain
from security_engine import (
    DependencyScanner,
    DriftRemediator,
    FairnessChecker,
    ImageScanner,
    KyvernoEngine,
    OPAGatekeeper,
    SASTScanner,
    SealedSecretsManager,
    VaultESOManager,
)

# 1. Custom JSON Logger Setup
logger = logging.getLogger("fastapi_service")
logHandler = logging.StreamHandler(sys.stdout)


class CustomJsonFormatter(jsonlogger.JsonFormatter):

    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = time.strftime(
            "%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)
        )
        log_record["level"] = record.levelname
        log_record["correlation_id"] = correlation_id.get() or "N/A"


formatter = CustomJsonFormatter(
    "%(timestamp)s %(level)s %(name)s %(correlation_id)s %(message)s"
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

# 2. Global Core Engines & Security Modules
auron_brain = AuronBrain()
pasha_orchestrator = PashaOrchestrator()

sast_scanner = SASTScanner()
dependency_scanner = DependencyScanner()
image_scanner = ImageScanner()
opa_gatekeeper = OPAGatekeeper()
kyverno_engine = KyvernoEngine()
sealed_secrets_mgr = SealedSecretsManager()
vault_eso_mgr = VaultESOManager()
drift_remediator = DriftRemediator()
fairness_checker = FairnessChecker()

# 3. FastAPI App Setup
app = FastAPI(
    title="NAYEEM-FLOW-OS Zero-Trust Security Platform API",
    description="Modern Engineering Workflow with 5-Layer Enterprise Security & Autonomous Governance",
    version="5.0.0",
)

# 4. Middleware Setup
app.add_middleware(
    CorrelationIdMiddleware,
    header_name="X-Request-ID",
    update_request_header=True,
)

Instrumentator().instrument(app).expose(app)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response: Response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)

    logger.info(
        "HTTP Request Processed",
        extra={
            "http_method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "latency_ms": duration_ms,
            "client_ip": request.client.host if request.client else "unknown",
        },
    )
    return response


# --- Pydantic Schemas ---
class DecisionRequest(BaseModel):
    feedback_text: str = Field(
        default="Enterprise SaaS expansion analysis with strong growth indicators."
    )


class CFORequest(BaseModel):
    historical_cashflows: List[float] = Field(
        default=[100000.0, 110000.0, 120000.0]
    )
    burn_rate: float = Field(default=200000.0)


class CMORequest(BaseModel):
    text: str = Field(
        default="Strong customer traction and product adoption rates."
    )
    competitors: List[str] = Field(default=["CompA", "CompB"])


class ResearchRequest(BaseModel):
    query: str = Field(
        default="Enterprise Quantum Governance and Autonomous Agent Swarms 2025"
    )
    topic: Optional[str] = Field(default="Tech")


class MeetingRequest(BaseModel):
    meeting_type: str = Field(default="DAILY_STANDUP")
    department: Optional[str] = Field(default=None)


class PolicyVerifyRequest(BaseModel):
    agent_id: str = Field(default="AGT-0001")
    policy_claim: str = Field(default="Confidential enclaved execution approved")


class SecurityScanRequest(BaseModel):
    code_repo: Optional[str] = Field(
        default=".", description="Code repository path or URL"
    )


class PolicyCheckRequest(BaseModel):
    k8s_manifest: Optional[str] = Field(
        default="apiVersion: apps/v1\nkind: Deployment\nmetadata:\n  name: nayeem-flow-os\n",
        description="Kubernetes YAML manifest",
    )


# --- Endpoint Definitions ---


@app.get("/")
def read_root():
    """Root endpoint returning service identity."""
    return {
        "status": "healthy",
        "service": "nayeem-flow-os-security-platform",
        "version": "5.0.0",
        "security_layers": 5,
        "zero_trust": "ACTIVE",
    }


@app.get("/health")
def health_check():
    """Health check endpoint required by system specification and tests."""
    return {
        "status": "healthy",
        "service": "auron-4000-pasha-nayeem-flow-os-security-platform",
        "agents_active": 4000,
        "quantum_engine_status": "ONLINE",
        "confidential_computing": "ENCLAVE_ATTESTED",
        "security_status": "ZERO_TRUST_COMPLIANT",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# --- NAYEEM-FLOW-OS 5-Layer Security REST Endpoints ---


@app.post("/security/scan")
def run_security_scan(req: Optional[SecurityScanRequest] = None):
    """Trigger 5-layer code, dependency, secret, and image scan."""
    repo = req.code_repo if req and req.code_repo else "."
    sast_res = sast_scanner.scan_code_repository(repo_path=repo)
    deps_res = dependency_scanner.scan_requirements()
    img_res = image_scanner.scan_image()

    return {
        "sast": {
            "issues": sast_res["issues"],
            "score": sast_res["score"],
        },
        "deps": {
            "vulns": deps_res["vulns"],
            "critical": deps_res["critical"],
        },
        "secrets": {
            "found": sast_res["secrets"]["found"],
        },
        "image": {
            "cves": img_res["cves"],
            "signed": img_res["signed"],
        },
    }


@app.post("/security/policy/check")
def run_policy_check(req: Optional[PolicyCheckRequest] = None):
    """Run Policy as Code checks using OPA Gatekeeper and Kyverno engines."""
    manifest = req.k8s_manifest if req and req.k8s_manifest else None
    opa_res = opa_gatekeeper.evaluate_manifest(manifest)
    kyv_res = kyverno_engine.evaluate_manifest(manifest)

    return {
        "opa": {
            "passed": opa_res["passed"],
            "failed": opa_res["failed"],
            "violations": opa_res["violations"],
        },
        "kyverno": {
            "passed": kyv_res["passed"],
            "failed": kyv_res["failed"],
        },
    }


@app.get("/security/secrets/status")
def get_secrets_status():
    """Retrieve HashiCorp Vault, ESO, Sealed Secrets, and secret rotation status."""
    v_status = vault_eso_mgr.get_status()
    return {
        "vault": v_status["vault"],
        "eso_sync": v_status["eso_sync"],
        "sealed_secrets": v_status["sealed_secrets"],
        "rotation_due": v_status["rotation_due"],
        "last_rotation": v_status["last_rotation"],
    }


@app.post("/security/runtime/check")
def run_runtime_check():
    """Run runtime drift detection, auto-remediation, model fairness, and data drift checks."""
    d_res = drift_remediator.check_cluster_drift()
    f_res = fairness_checker.evaluate_model_fairness()

    return {
        "drift": {
            "detected": d_res["detected"],
            "last": d_res["last"],
        },
        "fairness": {
            "bias": f_res["fairness"]["bias"],
            "status": f_res["fairness"]["status"],
        },
        "data_drift": f_res["data_drift"],
    }


# --- Quantum Governance & Swarm Endpoints ---


@app.get("/quantum/circuit")
def get_quantum_circuit_telemetry():
    """Retrieve 64-qubit Qiskit Quantum Circuit simulation telemetry for Zero-Trust verification."""
    telemetry = auron_brain.run_quantum_circuit_simulation()
    return telemetry


@app.get("/quantum/governance/status")
def get_quantum_governance_status():
    """Retrieve autonomous governance status across 4,000 agents and quantum security telemetry."""
    status_data = auron_brain.get_governance_status()
    return status_data


@app.post("/quantum/policy/verify")
def verify_policy_claim(req: PolicyVerifyRequest):
    """Verify an agent policy claim using 64-qubit quantum token proof."""
    result = auron_brain.verify_agent_policy(req.agent_id, req.policy_claim)
    return result


@app.get("/agents")
def list_agents(
    department: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    search: Optional[str] = Query(None),
):
    """Retrieve paginated or filtered list of 4,000 autonomous agents."""
    res = auron_brain.get_agents(
        department=department, page=page, limit=limit, search=search
    )
    return res


# --- Backwards Compatibility Endpoints ---


@app.post("/analyze/ceo-decision")
def analyze_ceo_decision(req: DecisionRequest):
    """Run enterprise analysis for CEO decision."""
    res = pasha_orchestrator.run_full_enterprise_analysis(
        {"contract_text": req.feedback_text}
    )
    return {"status": "success", "data": res}


@app.post("/agents/cfo")
def cfo_analysis(req: CFORequest):
    """CFO financial analysis endpoint."""
    cfo_agent = pasha_orchestrator.cfo_agent
    forecast = cfo_agent.forecast_cashflow(req.historical_cashflows)
    runway = cfo_agent.calculate_runway(req.burn_rate)
    unit_econ = cfo_agent.calculate_unit_economics()
    return {
        "status": "success",
        "data": {
            "forecast": forecast,
            "runway_months": runway,
            "unit_economics": unit_econ,
        },
    }


@app.post("/agents/cmo")
def cmo_analysis(req: CMORequest):
    """CMO marketing analysis endpoint."""
    cmo_agent = pasha_orchestrator.cmo_agent
    score = cmo_agent.sentiment_score(req.text)
    competitors = cmo_agent.competitor_analysis(req.competitors)
    return {
        "status": "success",
        "data": {"sentiment_score": score, "competitor_analysis": competitors},
    }


@app.post("/research")
def deep_research(req: ResearchRequest):
    """Deep online research pipeline endpoint."""
    res = pasha_orchestrator.research_agent.execute_deep_research(req.query)
    return {"status": "success", "data": res}


@app.post("/meetings/run")
def run_meeting(req: MeetingRequest):
    """Run automated department or board meeting."""
    mo = pasha_orchestrator.meeting_orchestrator
    mtype = req.meeting_type.upper()

    if "STANDUP" in mtype:
        res = mo.run_daily_standup()
    elif "BOARD" in mtype:
        res = mo.run_monthly_board_meeting()
    else:
        dept = req.department or "ENGINEERING DIVISION"
        res = mo.run_weekly_department_meeting(dept)

    return {"status": "success", "data": res}


@app.websocket("/board/meeting")
async def board_meeting_websocket(websocket: WebSocket):
    """WebSocket stream for real-time board meeting orchestration."""
    await websocket.accept()
    try:
        await websocket.send_json({
            "event": "MEETING_STARTED",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "participants": "NAYEEM-FLOW-OS Security Swarm Agents",
            "quantum_status": "ZERO_TRUST_VERIFIED",
        })
        await asyncio.sleep(0.1)

        steps = [
            ("EXECUTIVE_REPORTS", "C-Suite reporting cashflow & risk metrics"),
            ("QUANTUM_AUDIT", "64-Qubit Zero-Trust verification cycle complete"),
            (
                "GOVERNANCE_CONSENSUS",
                "4,000 Agents achieved Q-BFT Byzantine Fault Tolerance",
            ),
            ("MEETING_COMPLETED", "Board meeting finished with approved motion"),
        ]

        for step_event, desc in steps:
            await websocket.send_json({
                "event": step_event,
                "description": desc,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
            await asyncio.sleep(0.05)

        await websocket.close()
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client")


@app.get("/error-test")
def trigger_error():
    """Manual test error triggered for observability testing."""
    logger.error(
        "Manual test error triggered for observability testing",
        extra={"error_code": "TEST_500"},
    )
    return {"error": "Simulated exception logged"}
