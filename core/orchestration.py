"""Pasha Orchestrator initializing all 7 C-Suite Agents and running LangGraph CEO Decision flow."""

from typing import Dict, Any
from agents.cfo_agent import CFOAgent
from agents.cmo_agent import CMOAgent
from agents.coo_agent import COOAgent
from agents.chro_agent import CHROAgent
from agents.legal_agent import LegalAgent
from agents.investor_agent import InvestorAgent
from agents.strategy_agent import ceo_app, CEOState
from core.monte_carlo_50k import run_monte_carlo
from core.rag_engine import PashaRAGEngine


class PashaOrchestrator:
    """Master Orchestrator coordinating all 7 PASHA-OS autonomous enterprise agents."""

    def __init__(self) -> None:
        """Initialize all 7 C-suite agents and core vector/risk engines."""
        self.cfo_agent = CFOAgent()
        self.cmo_agent = CMOAgent()
        self.coo_agent = COOAgent()
        self.chro_agent = CHROAgent()
        self.legal_agent = LegalAgent()
        self.investor_agent = InvestorAgent()
        self.rag_engine = PashaRAGEngine()

    def run_full_enterprise_analysis(self, company_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Gather signals across all 7 C-Suite agents and execute CEO LangGraph decision graph.

        Args:
            company_data (Dict[str, Any], optional): Raw input company payload or context.

        Returns:
            Dict[str, Any]: Aggregated executive intelligence output and CEO decision.
        """
        company_data = company_data or {}

        # 1. Execute agent computations
        cfo_sig = self.cfo_agent.risk_assessment(company_data.get("historical_cashflows"))
        cmo_sig = self.cmo_agent.competitor_analysis(company_data.get("competitors"))
        cmo_sig["sentiment_score"] = self.cmo_agent.sentiment_score(
            company_data.get("feedback_text", "Strong market response and innovative growth.")
        )

        coo_sig = self.coo_agent.optimize_supply_chain(
            demands=company_data.get("demands"), costs=company_data.get("costs")
        )
        chro_sig = self.chro_agent.predict_attrition(company_data.get("employee_features"))
        legal_sig = self.legal_agent.analyze_contract(
            company_data.get("contract_text", "Compliant standard terms.")
        )
        investor_sig = self.investor_agent.synthesize_investor_deck_data(company_data.get("financials"))

        # 2. Run Monte Carlo simulation
        var_95, cvar_95, mean_pnl = run_monte_carlo()

        # 3. Form initial LangGraph input state
        initial_state: CEOState = {
            "cfo_signal": cfo_sig,
            "cmo_signal": cmo_sig,
            "coo_signal": coo_sig,
            "chro_signal": chro_sig,
            "legal_signal": legal_sig,
            "risk_score": 0.0,
            "decision": "PENDING",
        }

        # 4. Invoke LangGraph CEO Brain app
        graph_output = ceo_app.invoke(initial_state)

        return {
            "ceo_decision": graph_output.get("decision"),
            "overall_risk_score": graph_output.get("risk_score"),
            "monte_carlo_metrics": {
                "var_95": round(var_95, 2),
                "cvar_95": round(cvar_95, 2),
                "mean_pnl": round(mean_pnl, 2),
            },
            "agents_summary": {
                "cfo": cfo_sig,
                "cmo": cmo_sig,
                "coo": coo_sig,
                "chro": chro_sig,
                "legal": legal_sig,
                "investor": investor_sig,
            },
        }
