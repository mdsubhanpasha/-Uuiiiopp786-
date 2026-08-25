"""FastAPI Pydantic Request/Response Schemas for PASHA-OS 20-Agent REST API."""

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


class ResearchQueryInput(BaseModel):
    """Input schema for online research pipeline endpoint."""

    query: str = Field(..., description="Target query or research theme.")
    topic: Optional[str] = Field(default="Enterprise MNC OS")


class MeetingRunInput(BaseModel):
    """Input schema for triggering department meetings."""

    meeting_type: str = Field(
        default="DAILY_STANDUP", description="DAILY_STANDUP, WEEKLY_DEPARTMENT, or MONTHLY_BOARD"
    )
    department: Optional[str] = Field(
        default="ENGINEERING DIVISION", description="Target division for weekly meetings."
    )


class GenericAgentResponse(BaseModel):
    """Generic response wrapper for agent execution."""

    status: str = "success"
    data: Dict[str, Any]
