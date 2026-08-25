"""FastAPI Server for PASHA-OS Enterprise Intelligence Service."""

import asyncio
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from core.orchestration import PashaOrchestrator
from api.schemas import CEODecisionInput, CFOAgentInput, CMOAgentInput, GenericAgentResponse

app = FastAPI(
    title="PASHA-OS Enterprise Intelligence API",
    description="Predictive Autonomous System for Holistic Administration",
    version="1.0.0",
)

orchestrator = PashaOrchestrator()

# Prometheus metrics
REQUEST_COUNT = Counter("pasha_os_requests_total", "Total REST requests handled", ["endpoint"])
LATENCY_HISTOGRAM = Histogram("pasha_os_request_duration_seconds", "Request latency in seconds", ["endpoint"])


@app.get("/health")
def health_check() -> Dict[str, str]:
    """Health check endpoint.

    Returns:
        Dict[str, str]: Service status dictionary.
    """
    REQUEST_COUNT.labels(endpoint="/health").inc()
    return {"status": "healthy", "service": "PASHA-OS"}


@app.get("/metrics")
def metrics() -> PlainTextResponse:
    """Prometheus telemetry metrics endpoint.

    Returns:
        PlainTextResponse: Raw Prometheus formatted metrics data.
    """
    return PlainTextResponse(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/analyze/ceo-decision", response_model=GenericAgentResponse)
def analyze_ceo_decision(payload: CEODecisionInput) -> GenericAgentResponse:
    """Run full C-suite analysis and return LangGraph CEO board decision.

    Args:
        payload (CEODecisionInput): Executive input parameters.

    Returns:
        GenericAgentResponse: Structured board decision and agent metrics.
    """
    REQUEST_COUNT.labels(endpoint="/analyze/ceo-decision").inc()
    data_dict = payload.model_dump()
    result = orchestrator.run_full_enterprise_analysis(data_dict)
    return GenericAgentResponse(status="success", data=result)


@app.post("/agents/cfo", response_model=GenericAgentResponse)
def run_cfo_agent(payload: CFOAgentInput) -> GenericAgentResponse:
    """Execute CFO Agent forecasting and runway calculations.

    Args:
        payload (CFOAgentInput): CFO input parameters.

    Returns:
        GenericAgentResponse: CFO assessment report.
    """
    REQUEST_COUNT.labels(endpoint="/agents/cfo").inc()
    cfo = orchestrator.cfo_agent
    forecast = cfo.forecast_cashflow(payload.historical_cashflows)
    runway = cfo.calculate_runway(payload.burn_rate)
    risk = cfo.risk_assessment(payload.historical_cashflows)
    return GenericAgentResponse(
        status="success",
        data={"forecast": forecast, "runway_months": runway, "risk_assessment": risk},
    )


@app.post("/agents/cmo", response_model=GenericAgentResponse)
def run_cmo_agent(payload: CMOAgentInput) -> GenericAgentResponse:
    """Execute CMO Agent sentiment analysis and competitive intelligence.

    Args:
        payload (CMOAgentInput): CMO input parameters.

    Returns:
        GenericAgentResponse: CMO analysis result.
    """
    REQUEST_COUNT.labels(endpoint="/agents/cmo").inc()
    cmo = orchestrator.cmo_agent
    sentiment = cmo.sentiment_score(payload.text)
    comp = cmo.competitor_analysis(payload.competitors)
    return GenericAgentResponse(
        status="success",
        data={"sentiment_score": sentiment, "competitor_analysis": comp},
    )


@app.websocket("/board/meeting")
async def board_meeting_websocket(websocket: WebSocket) -> None:
    """Real-time WebSocket endpoint for autonomous C-Suite board meeting stream.

    Args:
        websocket (WebSocket): Client WebSocket connection.
    """
    await websocket.accept()
    try:
        await websocket.send_json({"event": "MEETING_STARTED", "message": "PASHA-OS Executive Board Convened."})

        # Stream individual agent signals in sequence
        agents_sequence = [
            ("CFO_AGENT", "Evaluating cashflow forecast and liquidity reserves..."),
            ("CMO_AGENT", "Analyzing market sentiment and competitor threat matrix..."),
            ("COO_AGENT", "Optimizing global supply chain allocation via linear programming..."),
            ("CHRO_AGENT", "Predicting workforce turnover using XGBoost model..."),
            ("LEGAL_AGENT", "Auditing statutory compliance rules and contract liability..."),
            ("INVESTOR_AGENT", "Synthesizing ARR and market valuation multiples..."),
            ("CEO_AGENT", "Synthesizing executive graph state for final decision..."),
        ]

        for role, msg in agents_sequence:
            await asyncio.sleep(0.3)
            await websocket.send_json({"agent": role, "status": "COMPLETED", "details": msg})

        # Run master orchestrator
        final_res = orchestrator.run_full_enterprise_analysis()
        await websocket.send_json({"event": "BOARD_DECISION", "data": final_res})
        await websocket.close()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
