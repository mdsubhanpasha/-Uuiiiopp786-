"""Data models and schemas for PASHA-OS core and agent system."""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class CashflowForecastRequest(BaseModel):
    """Request schema for CFO cashflow forecasting."""

    historical_data: List[float] = Field(..., description="Historical monthly cashflow numbers.")
    months_ahead: int = Field(default=12, description="Forecast horizon in months.")


class CashflowForecastResponse(BaseModel):
    """Response schema for CFO cashflow forecasting."""

    forecast: List[float] = Field(..., description="Forecasted monthly cashflows.")
    runway_months: float = Field(..., description="Calculated cash runway in months.")
    risk_level: str = Field(..., description="Financial risk classification.")


class SupplyChainOptimizationRequest(BaseModel):
    """Request schema for COO supply chain linear optimization."""

    demands: List[float] = Field(..., description="Demand requirements per warehouse/node.")
    costs: List[float] = Field(..., description="Unit transportation/production costs.")


class SupplyChainOptimizationResponse(BaseModel):
    """Response schema for COO supply chain optimization output."""

    optimal_cost: float = Field(..., description="Minimized total supply chain cost.")
    allocation: List[float] = Field(..., description="Optimal allocation units.")
    status: str = Field(..., description="Optimization status string.")


class AttritionPredictionRequest(BaseModel):
    """Request schema for CHRO employee attrition prediction."""

    employee_features: List[List[float]] = Field(..., description="Matrix of employee feature vectors.")


class AttritionPredictionResponse(BaseModel):
    """Response schema for CHRO attrition prediction output."""

    attrition_probabilities: List[float] = Field(..., description="Predicted attrition probability per employee.")
    high_risk_count: int = Field(..., description="Count of employees with >70% attrition risk.")


class ContractAnalysisRequest(BaseModel):
    """Request schema for Legal contract audit."""

    contract_text: str = Field(..., description="Raw string text of legal contract.")


class ContractAnalysisResponse(BaseModel):
    """Response schema for Legal contract analysis."""

    risk_score: float = Field(..., description="Assessed contract risk score between 0.0 and 1.0.")
    flagged_clauses: List[str] = Field(..., description="List of non-compliant or risky clauses.")


class CEODecisionRequest(BaseModel):
    """Request schema for overall CEO board decision invocation."""

    company_data: Dict[str, Any] = Field(default_factory=dict, description="Enterprise data payload.")


class CEODecisionResponse(BaseModel):
    """Response schema for CEO board decision invocation."""

    decision: str = Field(..., description="Strategic CEO decision: HALT_EXPANSION or APPROVE_GROWTH.")
    risk_score: float = Field(..., description="Overall aggregated enterprise risk score.")
    cfo_signal: Dict[str, Any] = Field(default_factory=dict)
    cmo_signal: Dict[str, Any] = Field(default_factory=dict)
    coo_signal: Dict[str, Any] = Field(default_factory=dict)
    chro_signal: Dict[str, Any] = Field(default_factory=dict)
    legal_signal: Dict[str, Any] = Field(default_factory=dict)
