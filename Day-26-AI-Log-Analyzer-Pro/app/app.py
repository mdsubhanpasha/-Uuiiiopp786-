"""
FastAPI Web Application for Day 26 - AI Log Analyzer Pro.
Exposes REST endpoints POST /analyze, GET /anomalies, POST /remediate, GET /metrics, GET /health.
"""

import logging
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Body, File, UploadFile, Request
from fastapi.responses import Response, JSONResponse
from pydantic import BaseModel, Field
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from app.analyzer import AILogAnalyzer

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("fastapi_app")

app = FastAPI(
    title="AI Log Analyzer Pro API",
    description="Production-Grade Log Parsing, Anomaly Detection, and Auto-Remediation Platform",
    version="1.0.0",
)

# Instantiate Orchestrator
analyzer = AILogAnalyzer()


class LogPayload(BaseModel):
    logs: List[str] = Field(..., description="List of log string entries to analyze")
    auto_remediate: bool = Field(default=True, description="Whether to automatically trigger remediation for detected anomalies")


class RemediatePayload(BaseModel):
    action: str = Field(..., description="Remediation action: 'cleanup', 'restart_pod', or 'scale_up'")
    details: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context or targeting metadata")


@app.get("/health", tags=["Health"])
def health_check():
    """Service health check endpoint."""
    return {"status": "healthy", "service": "AI Log Analyzer Pro", "version": "1.0.0"}


@app.post("/analyze", tags=["Log Analysis"])
async def analyze_logs(request: Request, file: Optional[UploadFile] = File(None)):
    """
    Parse uploaded logs or JSON payload, perform ML anomaly detection, and trigger auto-remediations.
    """
    raw_logs: List[str] = []
    auto_remediate = True

    content_type = request.headers.get("content-type", "")

    if "multipart/form-data" in content_type:
        form = await request.form()
        uploaded_file = form.get("file")
        if uploaded_file and hasattr(uploaded_file, "read"):
            content = await uploaded_file.read()
            raw_logs = [line for line in content.decode("utf-8").splitlines() if line.strip()]
        auto_remediate_param = form.get("auto_remediate")
        if auto_remediate_param is not None:
            auto_remediate = str(auto_remediate_param).lower() in ("true", "1", "yes")
    elif "application/json" in content_type:
        try:
            body_json = await request.json()
            if isinstance(body_json, dict):
                raw_logs = body_json.get("logs", [])
                auto_remediate = body_json.get("auto_remediate", True)
            elif isinstance(body_json, list):
                raw_logs = body_json
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid JSON format.")
    else:
        # Fallback to plain text body
        body_bytes = await request.body()
        if body_bytes:
            raw_logs = [line for line in body_bytes.decode("utf-8").splitlines() if line.strip()]

    result = analyzer.process_logs(raw_logs=raw_logs, auto_remediate=auto_remediate)
    return JSONResponse(status_code=200, content=result)


@app.get("/anomalies", tags=["Anomalies"])
def get_anomalies(limit: int = 50):
    """Retrieve history of detected anomalies."""
    anomalies = analyzer.get_recent_anomalies(limit=limit)
    return {
        "count": len(anomalies),
        "limit": limit,
        "anomalies": anomalies
    }


@app.post("/remediate", tags=["Remediation"])
def trigger_remediation(payload: RemediatePayload):
    """Manually trigger a specific remediation action (cleanup, restart_pod, scale_up)."""
    valid_actions = ["cleanup", "restart_pod", "scale_up"]
    if payload.action.lower() not in valid_actions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid action '{payload.action}'. Supported actions: {valid_actions}"
        )

    res = analyzer.remediator.execute_remediation(action=payload.action, details=payload.details)
    return res


@app.get("/metrics", tags=["Observability"])
def prometheus_metrics():
    """Expose Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
