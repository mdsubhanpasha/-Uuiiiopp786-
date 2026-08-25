"""CEO Strategy Agent powered by LangGraph StateGraph workflow execution.

Acts as THE CEO BRAIN aggregating executive C-Suite signals to reach strategic decisions.
"""

from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END


class CEOState(TypedDict):
    """Type definition for CEO State in LangGraph execution pipeline."""

    cfo_signal: Dict[str, Any]
    cmo_signal: Dict[str, Any]
    coo_signal: Dict[str, Any]
    chro_signal: Dict[str, Any]
    legal_signal: Dict[str, Any]
    risk_score: float
    decision: str


def cfo_node(state: CEOState) -> Dict[str, Any]:
    """CFO StateGraph node evaluating financial health signal.

    Args:
        state (CEOState): Current graph state.

    Returns:
        Dict[str, Any]: Updated state values.
    """
    cfo_data = state.get("cfo_signal") or {
        "forecast": [100000, 110000],
        "runway_months": 18.0,
        "risk_score": 0.2,
    }
    return {"cfo_signal": cfo_data}


def cmo_node(state: CEOState) -> Dict[str, Any]:
    """CMO StateGraph node evaluating marketing sentiment signal.

    Args:
        state (CEOState): Current graph state.

    Returns:
        Dict[str, Any]: Updated state values.
    """
    cmo_data = state.get("cmo_signal") or {
        "sentiment": 0.6,
        "risk_score": 0.3,
    }
    return {"cmo_signal": cmo_data}


def coo_node(state: CEOState) -> Dict[str, Any]:
    """COO StateGraph node evaluating operations and supply chain signal.

    Args:
        state (CEOState): Current graph state.

    Returns:
        Dict[str, Any]: Updated state values.
    """
    coo_data = state.get("coo_signal") or {
        "optimal_cost": 4500.0,
        "risk_score": 0.2,
    }
    return {"coo_signal": coo_data}


def chro_node(state: CEOState) -> Dict[str, Any]:
    """CHRO StateGraph node evaluating workforce attrition risk signal.

    Args:
        state (CEOState): Current graph state.

    Returns:
        Dict[str, Any]: Updated state values.
    """
    chro_data = state.get("chro_signal") or {
        "attrition_rate": 0.12,
        "risk_score": 0.3,
    }
    return {"chro_signal": chro_data}


def legal_node(state: CEOState) -> Dict[str, Any]:
    """Legal StateGraph node evaluating regulatory compliance risk signal.

    Args:
        state (CEOState): Current graph state.

    Returns:
        Dict[str, Any]: Updated state values.
    """
    legal_data = state.get("legal_signal") or {
        "compliance_status": "COMPLIANT",
        "risk_score": 0.2,
    }
    return {"legal_signal": legal_data}


def board_decision_node(state: CEOState) -> Dict[str, Any]:
    """CEO Board Decision node aggregating risk scores across nodes.

    Decision Rule:
        If aggregated weighted risk_score > 0.7 -> HALT_EXPANSION
        Else -> APPROVE_GROWTH

    Args:
        state (CEOState): Aggregated state from all executive C-Suite nodes.

    Returns:
        Dict[str, Any]: Final decision and calculated overall risk score.
    """
    cfo_risk = state.get("cfo_signal", {}).get("risk_score", 0.3)
    cmo_risk = state.get("cmo_signal", {}).get("risk_score", 0.3)
    coo_risk = state.get("coo_signal", {}).get("risk_score", 0.3)
    chro_risk = state.get("chro_signal", {}).get("risk_score", 0.3)
    legal_risk = state.get("legal_signal", {}).get("risk_score", 0.3)

    # Weighted average risk calculation
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
    """Build and compile the LangGraph CEO Strategy StateGraph application.

    Returns:
        Compiled LangGraph application instance.
    """
    workflow = StateGraph(CEOState)

    # Add agent nodes
    workflow.add_node("cfo_node", cfo_node)
    workflow.add_node("cmo_node", cmo_node)
    workflow.add_node("coo_node", coo_node)
    workflow.add_node("chro_node", chro_node)
    workflow.add_node("legal_node", legal_node)
    workflow.add_node("board_decision_node", board_decision_node)

    # Set workflow graph edges
    workflow.set_entry_point("cfo_node")
    workflow.add_edge("cfo_node", "cmo_node")
    workflow.add_edge("cmo_node", "coo_node")
    workflow.add_edge("coo_node", "chro_node")
    workflow.add_edge("chro_node", "legal_node")
    workflow.add_edge("legal_node", "board_decision_node")
    workflow.add_edge("board_decision_node", END)

    return workflow.compile()


ceo_app = create_ceo_app()
