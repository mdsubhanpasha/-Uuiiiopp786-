"""FastAPI Pydantic Request/Response Schemas for PASHA-OS REST API."""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field


class CEODecisionInput(BaseModel):
    """Input payload for CEO decision analysis."""

    historical_cashflows: Optional[List[float]] = Field(default=None)
    feedback_text: Optional[str] = Field(default="Strong growth in enterprise segment")
    contract_text: Optional[str] = Field(default="Standard compliant vendor terms")
    demands: Optional[List[float]] = Field(default=None)
    costs: Optional[List[float]] = Field(default=None)


class CFOAgentInput(BaseModel):
    """Input schema for CFO endpoint."""

    historical_cashflows: List[float] = Field(default_factory=lambda: [100000.0, 110000.0, 120000.0])
    burn_rate: float = Field(default=200000.0)


class CMOAgentInput(BaseModel):
    """Input schema for CMO endpoint."""

    text: str = Field(default="Market expansion is yielding excellent revenue growth")
    competitors: Optional[List[str]] = Field(default_factory=lambda: ["CompetitorA", "CompetitorB"])


class GenericAgentResponse(BaseModel):
    """Generic response wrapper for agent execution."""

    status: str = "success"
    data: Dict[str, Any]
