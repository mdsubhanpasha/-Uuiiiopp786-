"""FastAPI Server for PASHA-OS Enterprise 20-Agent Autonomous MNC Intelligence Service."""

import asyncio
from typing import Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from core.orchestration import PashaOrchestrator
from api.schemas import (
    CEODecisionInput,
    CFOAgentInput,
    CMOAgentInput,
    ResearchQueryInput,
    MeetingRunInput,
    GenericAgentResponse,
)

app = FastAPI(
    title="PASHA-OS Enterprise 20-Agent MNC API",
    description="Predictive Autonomous System for Holistic Administration - FAANG-grade 20 Agent MNC Operating System",
    version="2.0.0",
)

orchestrator = PashaOrchestrator()

# Prometheus telemetry metrics
REQUEST_COUNT = Counter("pasha_os_requests_total", "Total REST requests handled", ["endpoint"])
LATENCY_HISTOGRAM = Histogram("pasha_os_request_duration_seconds", "Request latency in seconds", ["endpoint"])


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint.

    Returns:
        Dict[str, Any]: Service status dictionary.
    """
    REQUEST_COUNT.labels(endpoint="/health").inc()
    return {"status": "healthy", "service": "PASHA-OS", "agents_active": 20}


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
        GenericAgentResponse: Structured board decision and 20-agent MNC metrics.
    """
    REQUEST_COUNT.labels(endpoint="/analyze/ceo-decision").inc()
    data_dict = payload.model_dump()
    result = orchestrator.run_full_enterprise_analysis(data_dict)
    return GenericAgentResponse(status="success", data=result)


@app.post("/agents/cfo", response_model=GenericAgentResponse)
def run_cfo_agent(payload: CFOAgentInput) -> GenericAgentResponse:
    """Execute CFO Agent high-precision Decimal forecasting, P&L, unit economics, and runway calculations.

    Args:
        payload (CFOAgentInput): CFO input parameters.

    Returns:
        GenericAgentResponse: CFO assessment report.
    """
    REQUEST_COUNT.labels(endpoint="/agents/cfo").inc()
    cfo = orchestrator.cfo_agent
    forecast = cfo.forecast_cashflow(payload.historical_cashflows)
    runway = cfo.calculate_runway(payload.burn_rate)
    unit_econ = cfo.calculate_unit_economics()
    risk = cfo.risk_assessment(payload.historical_cashflows)
    return GenericAgentResponse(
        status="success",
        data={
            "forecast": forecast,
            "runway_months": runway,
            "unit_economics": unit_econ,
            "risk_assessment": risk,
        },
    )


@app.post("/agents/cmo", response_model=GenericAgentResponse)
def run_cmo_agent(payload: CMOAgentInput) -> GenericAgentResponse:
    """Execute CMO Agent sentiment analysis, GTM strategy, and competitive intelligence.

    Args:
        payload (CMOAgentInput): CMO input parameters.

    Returns:
        GenericAgentResponse: CMO analysis result.
    """
    REQUEST_COUNT.labels(endpoint="/agents/cmo").inc()
    cmo = orchestrator.cmo_agent
    sentiment = cmo.sentiment_score(payload.text)
    gtm = cmo.analyze_gtm_and_campaign()
    comp = cmo.competitor_analysis(payload.competitors)
    return GenericAgentResponse(
        status="success",
        data={"sentiment_score": sentiment, "gtm_strategy": gtm, "competitor_analysis": comp},
    )


@app.post("/research", response_model=GenericAgentResponse)
def execute_research(payload: ResearchQueryInput) -> GenericAgentResponse:
    """Execute online research pipeline using Tavily/DuckDuckGo + summarization.

    Args:
        payload (ResearchQueryInput): Search query input.

    Returns:
        GenericAgentResponse: Online research dossier.
    """
    REQUEST_COUNT.labels(endpoint="/research").inc()
    res = orchestrator.research_agent.execute_deep_research(payload.query)
    return GenericAgentResponse(status="success", data=res)


@app.post("/meetings/run", response_model=GenericAgentResponse)
def run_meeting(payload: MeetingRunInput) -> GenericAgentResponse:
    """Trigger Daily Standup, Weekly Department Meeting, or Monthly Board Meeting.

    Args:
        payload (MeetingRunInput): Meeting parameters.

    Returns:
        GenericAgentResponse: Meeting transcript and summary.
    """
    REQUEST_COUNT.labels(endpoint="/meetings/run").inc()
    orchestrator_m = orchestrator.meeting_orchestrator
    m_type = payload.meeting_type.upper()

    if m_type == "DAILY_STANDUP":
        transcript = orchestrator_m.run_daily_standup()
    elif m_type == "WEEKLY_DEPARTMENT":
        transcript = orchestrator_m.run_weekly_department_meeting(payload.department or "ENGINEERING DIVISION")
    else:
        transcript = orchestrator_m.run_monthly_board_meeting()

    return GenericAgentResponse(status="success", data=transcript)


@app.websocket("/board/meeting")
async def board_meeting_websocket(websocket: WebSocket) -> None:
    """Real-time WebSocket endpoint for autonomous 20-Agent MNC meeting stream.

    Args:
        websocket (WebSocket): Client WebSocket connection.
    """
    await websocket.accept()
    try:
        await websocket.send_json({"event": "MEETING_STARTED", "message": "PASHA-OS 20-Agent MNC Board Convened."})

        divisions_sequence = [
            ("CORE C-SUITE", "CEO, CFO, CTO, CMO, COO, CHRO, CLO deliberating strategic alignment..."),
            ("ENGINEERING DIVISION", "Staff Engineer, QA, DevOps, Security auditing system design..."),
            ("DATA & AI DIVISION", "Data Scientist, ML Engineer, Analytics, Research tracking MLflow..."),
            ("PRODUCT & GROWTH DIVISION", "Product Manager, UX Research, Growth Hacker prioritizing backlog..."),
            ("CUSTOMER & SALES DIVISION", "Sales Strategist, Customer Success evaluating lead scores..."),
            ("QUALITY ASSURANCE", "Validator & Red Team Critic auditing decision integrity..."),
        ]

        for division, msg in divisions_sequence:
            await asyncio.sleep(0.2)
            await websocket.send_json({"division": division, "status": "DELIBERATING", "details": msg})

        # Run master orchestrator
        final_res = orchestrator.run_full_enterprise_analysis()
        await websocket.send_json({"event": "BOARD_DECISION", "data": final_res})
        await websocket.close()
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close()
