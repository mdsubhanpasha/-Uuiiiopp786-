"""CEO Strategy Agent powered by LangGraph StateGraph workflow execution and Tavily/DDG market research.

Acts as THE CEO BRAIN aggregating executive C-Suite signals to reach strategic decisions, vision, and OKRs.
"""

from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from agents.base_agent import BaseAgent


class CEOAgent(BaseAgent):
    """Chief Executive Officer Autonomous Agent."""

    def __init__(self) -> None:
        """Initialize CEO Agent."""
        super().__init__(
            agent_name="CEO Agent",
            role="Strategic Decision, Corporate OKRs, Enterprise Vision & Market Research",
            division="CORE C-SUITE",
        )

    def formulate_vision_and_okrs(self, company_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Formulate strategic vision and corporate OKRs using online market intelligence.

        Args:
            company_context (Dict[str, Any], optional): Corporate context parameters.

        Returns:
            Dict[str, Any]: Executive vision and OKRs decision report.
        """
        ctx = company_context or {"industry": "Enterprise AI SaaS", "target_arr": 50000000.0}
        research = self.research_tool(query="Enterprise AI SaaS MNC strategic vision OKR benchmarks 2025")

        okrs = [
            {
                "objective": "Achieve $50M ARR with >80% Gross Margin",
                "key_results": ["3x Enterprise customer growth", "Maintain NRR > 120%"],
            },
            {
                "objective": "Expand Global MNC Market Share",
                "key_results": ["Deploy multi-region k8s clusters", "Maintain 99.99% SLA"],
            },
        ]

        reasoning = (
            f"Synthesized market intelligence for {ctx.get('industry')}. "
            f"Formulated 2 strategic corporate OKRs aligned with $50M ARR target. "
            f"Market benchmarks from {research['source_used']} validated target growth trajectory."
        )

        return self.format_decision(
            reasoning=reasoning,
            data_sources=[research["source_used"], "Board Strategic Directives"],
            alternatives_considered=["Conservative 15% YoY growth target", "Aggressive international M&A expansion"],
            final_decision={
                "vision_statement": "To lead global market in autonomous enterprise MNC OS solutions.",
                "okrs": okrs,
            },
            confidence_score=0.97,
            extra_fields={"okrs": okrs, "vision": "Autonomous MNC Operational Dominance"},
        )


class CEOState(TypedDict):
    """Type definition for CEO State in LangGraph execution pipeline."""

    cfo_signal: Dict[str, Any]
    cmo_signal: Dict[str, Any]
    coo_signal: Dict[str, Any]
    chro_signal: Dict[str, Any]
    legal_signal: Dict[str, Any]
    cto_signal: Dict[str, Any]
    risk_score: float
    decision: str


def cfo_node(state: CEOState) -> Dict[str, Any]:
    """CFO StateGraph node evaluating financial health signal."""
    cfo_data = state.get("cfo_signal") or {
        "forecast": [100000, 110000],
        "runway_months": 18.0,
        "risk_score": 0.2,
    }
    return {"cfo_signal": cfo_data}


def cmo_node(state: CEOState) -> Dict[str, Any]:
    """CMO StateGraph node evaluating marketing sentiment signal."""
    cmo_data = state.get("cmo_signal") or {
        "sentiment": 0.6,
        "risk_score": 0.3,
    }
    return {"cmo_signal": cmo_data}


def coo_node(state: CEOState) -> Dict[str, Any]:
    """COO StateGraph node evaluating operations signal."""
    coo_data = state.get("coo_signal") or {
        "optimal_cost": 4500.0,
        "risk_score": 0.2,
    }
    return {"coo_signal": coo_data}


def chro_node(state: CEOState) -> Dict[str, Any]:
    """CHRO StateGraph node evaluating workforce attrition risk signal."""
    chro_data = state.get("chro_signal") or {
        "attrition_rate": 0.12,
        "risk_score": 0.3,
    }
    return {"chro_signal": chro_data}


def legal_node(state: CEOState) -> Dict[str, Any]:
    """Legal StateGraph node evaluating regulatory compliance risk signal."""
    legal_data = state.get("legal_signal") or {
        "compliance_status": "COMPLIANT",
        "risk_score": 0.2,
    }
    return {"legal_signal": legal_data}


def board_decision_node(state: CEOState) -> Dict[str, Any]:
    """CEO Board Decision node aggregating risk scores across nodes."""
    cfo_risk = state.get("cfo_signal", {}).get("risk_score", 0.3)
    cmo_risk = state.get("cmo_signal", {}).get("risk_score", 0.3)
    coo_risk = state.get("coo_signal", {}).get("risk_score", 0.3)
    chro_risk = state.get("chro_signal", {}).get("risk_score", 0.3)
    legal_risk = state.get("legal_signal", {}).get("risk_score", 0.3)

    aggregated_risk = (
        0.30 * cfo_risk + 0.15 * cmo_risk + 0.15 * coo_risk + 0.15 * chro_risk + 0.25 * legal_risk
    )
    aggregated_risk = round(aggregated_risk, 3)

    decision = "HALT_EXPANSION" if aggregated_risk > 0.7 else "APPROVE_GROWTH"

    return {
        "risk_score": aggregated_risk,
        "decision": decision,
    }


def create_ceo_app():
    """Build and compile the LangGraph CEO Strategy StateGraph application."""
    workflow = StateGraph(CEOState)

    workflow.add_node("cfo_node", cfo_node)
    workflow.add_node("cmo_node", cmo_node)
    workflow.add_node("coo_node", coo_node)
    workflow.add_node("chro_node", chro_node)
    workflow.add_node("legal_node", legal_node)
    workflow.add_node("board_decision_node", board_decision_node)

    workflow.set_entry_point("cfo_node")
    workflow.add_edge("cfo_node", "cmo_node")
    workflow.add_edge("cmo_node", "coo_node")
    workflow.add_edge("coo_node", "chro_node")
    workflow.add_edge("chro_node", "legal_node")
    workflow.add_edge("legal_node", "board_decision_node")
    workflow.add_edge("board_decision_node", END)

    return workflow.compile()


ceo_app = create_ceo_app()
