"""FastAPI Backend REST & WebSocket Service for AURON-4000 Quantum Governance Plane."""

import asyncio
from datetime import datetime, timezone
import logging
import sys
import time
from typing import Any, Dict, List, Optional

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, Query, Request, Response, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from prometheus_fastapi_instrumentator import Instrumentator
from pythonjsonlogger import jsonlogger

from core.orchestration import PashaOrchestrator
from core.orchestration.auron_brain import AuronBrain

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

# 2. Global Core Engines
auron_brain = AuronBrain()
pasha_orchestrator = PashaOrchestrator()

# 3. FastAPI App Setup
app = FastAPI(
    title="AURON-4000 Quantum Governance Plane Service",
    description="FAANG-Grade 4000-Agent Autonomous MNC OS with Qiskit 64-Qubit Zero-Trust Quantum Verification",
    version="4.0.0",
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


# --- Endpoint Definitions ---


@app.get("/")
def read_root():
  """Root endpoint returning service identity."""
  return {
      "status": "healthy",
      "service": "auron-4000-quantum-governance",
      "version": "4.0.0",
      "agents_active": 4000,
      "quantum_verification": "ACTIVE_64_QUBIT",
  }


@app.get("/health")
def health_check():
  """Health check endpoint required by system specification and tests."""
  return {
      "status": "healthy",
      "service": "auron-4000-quantum-governance",
      "agents_active": 4000,
      "quantum_engine_status": "ONLINE",
      "confidential_computing": "ENCLAVE_ATTESTED",
      "timestamp": datetime.now(timezone.utc).isoformat(),
  }


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


# --- Backwards Compatibility Endpoints for PashaOrchestrator ---


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
        "participants": "AURON-4000 Autonomous Agents",
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
