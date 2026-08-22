"""Data models and schemas for FinAgent-Ops financial reconciliation engine."""

from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field


class LedgerTransaction(BaseModel):
    """Schema representing an enterprise ledger transaction record."""

    transaction_id: str = Field(
        ..., description="Unique ledger transaction ID"
    )
    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    amount: float = Field(..., description="Monetary transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    vendor: str = Field(..., description="Vendor or merchant name")
    description: str = Field(
        default="", description="Transaction detailed description"
    )
    reference_id: str = Field(
        default="", description="ERP cross-reference identifier"
    )


class BankTransaction(BaseModel):
    """Schema representing a bank statement transaction entry."""

    bank_txn_id: str = Field(..., description="Unique bank transaction ID")
    booking_date: str = Field(
        ..., description="Bank booking date (YYYY-MM-DD)"
    )
    amount: float = Field(..., description="Posted transaction amount")
    currency: str = Field(default="USD", description="Currency code")
    counterparty: str = Field(
        ..., description="Counterparty or payee name on statement"
    )
    reference_code: str = Field(
        default="", description="Bank reference code or check number"
    )
    status: str = Field(
        default="POSTED", description="Transaction status (e.g., POSTED)"
    )


class ReconciliationDiscrepancy(BaseModel):
    """Schema representing a reconciliation mismatch."""

    discrepancy_id: str = Field(..., description="Unique discrepancy ID")
    ledger_txn_id: Optional[str] = Field(
        default=None, description="Associated ledger transaction ID"
    )
    bank_txn_id: Optional[str] = Field(
        default=None, description="Associated bank transaction ID"
    )
    discrepancy_type: str = Field(
        ..., description="Type of mismatch (e.g. AMOUNT_MISMATCH)"
    )
    ledger_amount: Optional[float] = Field(
        default=None, description="Amount recorded in ledger"
    )
    bank_amount: Optional[float] = Field(
        default=None, description="Amount recorded in bank statement"
    )
    amount_difference: float = Field(
        default=0.0, description="Absolute difference in transaction amounts"
    )
    is_anomaly: bool = Field(
        default=False, description="Whether ML Isolation Forest flagged"
    )
    anomaly_score: float = Field(
        default=0.0, description="Statistical anomaly score"
    )
    details: str = Field(
        default="", description="Descriptive context regarding mismatch"
    )


class ForensicRiskEntry(BaseModel):
    """Schema representing LLM forensic audit analysis output."""

    discrepancy_id: str = Field(..., description="Target discrepancy ID")
    risk_level: str = Field(
        ..., description="Assigned risk level: Low | Medium | High | Critical"
    )
    confidence_score: float = Field(
        ..., description="Auditor confidence score (0.0 - 1.0)"
    )
    root_cause_explanation: str = Field(
        ..., description="Synthesized root cause explanation"
    )
    recommended_action: str = Field(
        ..., description="Actionable remediation steps"
    )
    cot_reasoning_trace: List[str] = Field(
        default_factory=list, description="Chain-of-thought reasoning steps"
    )


class AuditReportSummary(BaseModel):
    """Aggregate summary statistics of the financial reconciliation run."""

    total_ledger_records: int = Field(..., description="Total ledger rows")
    total_bank_records: int = Field(
        ..., description="Total bank statement rows"
    )
    matched_count: int = Field(..., description="Successfully matched count")
    discrepancy_count: int = Field(
        ..., description="Total mismatches detected"
    )
    anomaly_count: int = Field(
        ..., description="Total ML isolation anomalies"
    )
    high_risk_count: int = Field(
        ..., description="High/Critical risk count from forensic audit"
    )
    total_ledger_amount: float = Field(
        ..., description="Sum of ledger amounts"
    )
    total_bank_amount: float = Field(
        ..., description="Sum of bank statement amounts"
    )


class FinancialAuditState(TypedDict):
    """State schema for LangGraph supervisor orchestrator graph state."""

    ledger_data: List[Dict[str, Any]]
    bank_data: List[Dict[str, Any]]
    normalized_ledger: List[Dict[str, Any]]
    normalized_bank: List[Dict[str, Any]]
    ingestion_errors: List[str]
    discrepancies: List[Dict[str, Any]]
    audit_results: List[Dict[str, Any]]
    report_summary: Dict[str, Any]
    pdf_report_path: Optional[str]
    messages: List[str]


class ReconcileRequest(BaseModel):
    """API request payload for financial reconciliation workflow."""

    ledger_csv_path: Optional[str] = Field(
        default="data/sample_ledger.csv",
        description="Path to ledger CSV file",
    )
    bank_csv_path: Optional[str] = Field(
        default="data/bank_statement.csv",
        description="Path to bank statement CSV file",
    )


class ReconcileResponse(BaseModel):
    """API response payload containing summary and discrepancy artifacts."""

    status: str = Field(..., description="Execution status")
    summary: Dict[str, Any] = Field(..., description="Audit run summary")
    discrepancy_count: int = Field(
        ..., description="Total detected discrepancies"
    )
    audit_results: List[Dict[str, Any]] = Field(
        ..., description="Forensic audit outputs"
    )
    pdf_report_path: Optional[str] = Field(
        default=None, description="Path to generated PDF report"
    )


class DeployRequest(BaseModel):
    """API request payload for script automation execution."""

    commit_message: Optional[str] = Field(
        default="Deploy FinAgent-Ops release",
        description="Git commit message",
    )
    dry_run: bool = Field(
        default=True, description="Execute in dry-run mode"
    )


class DeployResponse(BaseModel):
    """API response payload for automation deploy scripts."""

    status: str = Field(..., description="Deployment result status")
    details: Dict[str, Any] = Field(..., description="Output details")
