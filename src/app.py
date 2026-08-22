"""CloudNative DevOps Day 3 Production FastAPI Application.

Provides health checks, metrics endpoints, and simulated transaction
processing for enterprise CloudNative operations.
"""

from datetime import datetime, timezone
import time
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Application start time for uptime calculation
START_TIME = time.time()

app = FastAPI(
    title="CloudNative-Ops-Day3 Microservice",
    description="Production FastAPI service with automated container security",
    version="1.0.0",
)

# In-memory metrics storage
METRICS_DATA = {
    "total_requests": 0,
    "transactions_processed": 0,
    "total_transaction_amount": 0.0,
    "errors_count": 0,
}


class TransactionRequest(BaseModel):
    """Pydantic schema for transaction processing requests."""

    transaction_id: str = Field(
        ...,
        description="Unique identifier for the transaction",
        json_schema_extra={"example": "TX-99823"},
    )
    account_id: str = Field(
        ...,
        description="Target account identifier",
        json_schema_extra={"example": "ACC-10023"},
    )
    amount: float = Field(
        ...,
        gt=0.0,
        description="Transaction monetary amount (must be positive)",
        json_schema_extra={"example": 250.50},
    )
    currency: str = Field(
        default="USD",
        description="ISO currency code",
        json_schema_extra={"example": "USD"},
    )
    transaction_type: str = Field(
        default="CREDIT",
        description="Type of transaction (e.g., CREDIT, DEBIT)",
        json_schema_extra={"example": "CREDIT"},
    )


class TransactionResponse(BaseModel):
    """Pydantic schema for transaction processing responses."""

    status: str
    transaction_id: str
    processed_at: str
    amount: float
    currency: str
    reference_hash: str


@app.get("/", status_code=status.HTTP_200_OK)
def get_root_info() -> Dict[str, Any]:
    """Retrieve service metadata and API information."""
    METRICS_DATA["total_requests"] += 1
    return {
        "service": "devops-day3-cloudnative-pipeline",
        "version": "1.0.0",
        "status": "active",
        "architecture": "Multi-stage Docker / FastAPI",
        "documentation": "/docs",
    }


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> Dict[str, Any]:
    """Perform health check and report system status and uptime."""
    METRICS_DATA["total_requests"] += 1
    uptime_seconds = round(time.time() - START_TIME, 2)
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "uptime_seconds": uptime_seconds,
        "environment": "production",
    }


@app.get("/metrics", status_code=status.HTTP_200_OK)
def get_metrics() -> Dict[str, Any]:
    """Retrieve application metrics and operational statistics."""
    METRICS_DATA["total_requests"] += 1
    uptime_seconds = round(time.time() - START_TIME, 2)
    return {
        "metrics": METRICS_DATA,
        "system_status": "OPERATIONAL",
        "uptime_seconds": uptime_seconds,
        "container_security": "HARDENED",
    }


@app.post("/transaction", status_code=status.HTTP_201_CREATED)
def process_transaction(
    payload: TransactionRequest,
) -> TransactionResponse:
    """Simulate monetary transaction processing with validation."""
    METRICS_DATA["total_requests"] += 1

    if payload.amount <= 0:
        METRICS_DATA["errors_count"] += 1
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction amount must be strictly greater than zero.",
        )

    METRICS_DATA["transactions_processed"] += 1
    METRICS_DATA["total_transaction_amount"] += payload.amount

    now_iso = datetime.now(timezone.utc).isoformat()
    raw_str = payload.transaction_id + now_iso
    ref_hash = f"HASH-{hash(raw_str) & 0xFFFFFFFF:08X}"

    return TransactionResponse(
        status="SUCCESS",
        transaction_id=payload.transaction_id,
        processed_at=now_iso,
        amount=payload.amount,
        currency=payload.currency,
        reference_hash=ref_hash,
    )
