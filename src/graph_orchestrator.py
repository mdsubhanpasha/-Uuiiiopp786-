"""Supervisor Orchestrator using LangGraph StateGraph."""

import logging
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from src.agents.audit_agent import ForensicAuditAgent
from src.agents.ingest_agent import IngestionAgent
from src.agents.recon_agent import ReconciliationAgent
from src.agents.report_agent import ReportAgent
from src.models import FinancialAuditState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GraphOrchestrator")


class FinAgentOrchestrator:
    """LangGraph StateGraph managing workflow state transitions."""

    def __init__(self) -> None:
        """Initialize agents and compile the LangGraph workflow."""
        self.ingest_agent = IngestionAgent()
        self.recon_agent = ReconciliationAgent()
        self.audit_agent = ForensicAuditAgent()
        self.report_agent = ReportAgent()
        self.graph = self._build_graph()

    def node_ingest(self, state: FinancialAuditState) -> Dict[str, Any]:
        """Node 1: Ingestion & Validation Agent execution.

        Args:
            state: FinancialAuditState instance.

        Returns:
            State updates dict.
        """
        logger.info("[Orchestrator] Executing Ingestion Node...")
        ledger_path = state.get("ledger_path", "data/sample_ledger.csv")
        bank_path = state.get("bank_path", "data/bank_statement.csv")

        res = self.ingest_agent.process(ledger_path, bank_path)
        messages = state.get("messages", [])
        messages.append(
            f"[IngestNode] Loaded {len(res['normalized_ledger'])} ledger and "
            f"{len(res['normalized_bank'])} bank statement records."
        )

        return {
            "normalized_ledger": res["normalized_ledger"],
            "normalized_bank": res["normalized_bank"],
            "ingestion_errors": res["ingestion_errors"],
            "messages": messages,
        }

    def node_reconcile(self, state: FinancialAuditState) -> Dict[str, Any]:
        """Node 2: Reconciliation & Anomaly Agent execution.

        Args:
            state: FinancialAuditState instance.

        Returns:
            State updates dict.
        """
        logger.info("[Orchestrator] Executing Reconciliation Node...")
        l_records = state.get("normalized_ledger", [])
        b_records = state.get("normalized_bank", [])

        matched, discrepancies = self.recon_agent.reconcile(
            l_records, b_records
        )

        messages = state.get("messages", [])
        messages.append(
            f"[ReconNode] Matched {len(matched)} transactions; "
            f"flagged {len(discrepancies)} discrepancies."
        )

        return {
            "matched_records": matched,
            "discrepancies": discrepancies,
            "messages": messages,
        }

    def node_audit(self, state: FinancialAuditState) -> Dict[str, Any]:
        """Node 3: Forensic Audit LLM Agent execution.

        Args:
            state: FinancialAuditState instance.

        Returns:
            State updates dict.
        """
        logger.info("[Orchestrator] Executing Forensic Audit Node...")
        discrepancies = state.get("discrepancies", [])
        l_records = state.get("normalized_ledger", [])
        b_records = state.get("normalized_bank", [])

        audit_results = self.audit_agent.process(
            discrepancies, l_records, b_records
        )

        messages = state.get("messages", [])
        messages.append(
            f"[AuditNode] Evaluated {len(audit_results)} discrepancies with "
            "tool-calling and CoT reasoning."
        )

        return {
            "audit_results": audit_results,
            "messages": messages,
        }

    def node_report(self, state: FinancialAuditState) -> Dict[str, Any]:
        """Node 4: Report & Artifact Generation Agent execution.

        Args:
            state: FinancialAuditState instance.

        Returns:
            State updates dict.
        """
        logger.info("[Orchestrator] Executing Report Generation Node...")
        l_records = state.get("normalized_ledger", [])
        b_records = state.get("normalized_bank", [])
        matched = state.get("matched_records", [])
        discrepancies = state.get("discrepancies", [])
        audit_results = state.get("audit_results", [])

        res = self.report_agent.process(
            l_records, b_records, matched, discrepancies, audit_results
        )

        messages = state.get("messages", [])
        messages.append(
            f"[ReportNode] Exported PDF report to '{res['pdf_report_path']}' "
            "and JSON artifact."
        )

        return {
            "report_summary": res["summary"],
            "pdf_report_path": res["pdf_report_path"],
            "messages": messages,
        }

    def _build_graph(self) -> Any:
        """Construct LangGraph StateGraph defining agent transitions.

        Returns:
            Compiled StateGraph executable object.
        """
        builder = StateGraph(FinancialAuditState)

        builder.add_node("ingest", self.node_ingest)
        builder.add_node("reconcile", self.node_reconcile)
        builder.add_node("audit", self.node_audit)
        builder.add_node("report", self.node_report)

        builder.add_edge(START, "ingest")
        builder.add_edge("ingest", "reconcile")
        builder.add_edge("reconcile", "audit")
        builder.add_edge("audit", "report")
        builder.add_edge("report", END)

        return builder.compile()

    def run(
        self,
        ledger_path: str = "data/sample_ledger.csv",
        bank_path: str = "data/bank_statement.csv",
    ) -> FinancialAuditState:
        """Execute end-to-end multi-agent orchestration workflow.

        Args:
            ledger_path: Path to ledger CSV file.
            bank_path: Path to bank statement CSV file.

        Returns:
            Final state containing summary, audit outputs, and PDF report path.
        """
        initial_state: Dict[str, Any] = {
            "ledger_path": ledger_path,
            "bank_path": bank_path,
            "ledger_data": [],
            "bank_data": [],
            "normalized_ledger": [],
            "normalized_bank": [],
            "ingestion_errors": [],
            "discrepancies": [],
            "audit_results": [],
            "report_summary": {},
            "pdf_report_path": None,
            "messages": [
                "[System] Initializing FinAgent-Ops Orchestration Graph"
            ],
        }

        final_state = self.graph.invoke(initial_state)
        return final_state
