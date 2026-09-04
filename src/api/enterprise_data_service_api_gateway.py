"""
Enterprise Data Service API Gateway Module.

FastAPI REST endpoints:
- GET /
- GET /live/telemetry
- GET /live/profiling
- POST /fabric/ingest

Uses eval() / query() and to_json() for high-performance live data delivery.
"""

import json
import os
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, Response

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.orchestration.enterprise_orchestration_pipeline_controller import run_master_enterprise_pipeline
from src.core.data_profiling_and_quality_assessment_engine import assess_dataframe_quality

app = FastAPI(
    title="NAYEEM-ELDF: Enterprise Live Data Fabric API Gateway",
    description="Real-Time Data Intelligence & Feature Factory Gateway",
    version="1.0.0"
)

# Cache pipeline result in memory
CACHE = {}


def _get_cached_pipeline():
    if "data" not in CACHE:
        CACHE["data"] = run_master_enterprise_pipeline()
    return CACHE["data"]


@app.get("/")
def root_endpoint():
    """Root metadata & service status."""
    return {
        "service": "NAYEEM-ELDF: Enterprise Live Data Fabric",
        "status": "OPERATIONAL",
        "version": "1.0.0",
        "endpoints": ["/live/telemetry", "/live/profiling", "/fabric/ingest"]
    }


@app.get("/live/telemetry")
def get_live_telemetry():
    """Returns live serialized telemetry payload using df.to_json()."""
    data = _get_cached_pipeline()
    telemetry_df = data["telemetry"]
    json_str = telemetry_df.to_json(orient="records", date_format="iso")
    return Response(content=json_str, media_type="application/json")


@app.get("/live/profiling")
def get_live_profiling():
    """Returns real-time data profiling and quality metrics dict."""
    data = _get_cached_pipeline()
    telemetry_df = data["telemetry"]
    quality = assess_dataframe_quality(telemetry_df)

    # Format shape and types for JSON output
    output = {
        "shape": list(quality["shape"]),
        "missing_count": quality["missing_count"],
        "duplicate_count": quality["duplicate_count"],
        "dtypes": {str(k): str(v) for k, v in quality["dtypes"].items()}
    }
    return JSONResponse(content=output)


@app.post("/fabric/ingest")
def trigger_fabric_ingestion(query_expr: str = Query(default=None)):
    """Triggers live ingestion refresh and evaluates vector query filters."""
    global CACHE
    CACHE["data"] = run_master_enterprise_pipeline()
    telemetry_df = CACHE["data"]["telemetry"]

    if query_expr:
        try:
            filtered_df = telemetry_df.query(query_expr)
            json_str = filtered_df.to_json(orient="records", date_format="iso")
            return Response(content=json_str, media_type="application/json")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid query expression: {str(e)}")

    json_str = telemetry_df.head(10).to_json(orient="records", date_format="iso")
    return Response(content=json_str, media_type="application/json")
