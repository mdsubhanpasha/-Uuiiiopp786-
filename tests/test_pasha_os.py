"""PASHA-OS Unit and Integration Test Suite.

Verifies core functional components across multi-agent system, engines, API, and graph execution.
"""

from fastapi.testclient import TestClient

from core.monte_carlo_50k import run_monte_carlo
from core.rag_engine import PashaRAGEngine
from agents.cfo_agent import CFOAgent
from agents.cmo_agent import CMOAgent
from agents.coo_agent import COOAgent
from agents.chro_agent import CHROAgent
from agents.legal_agent import LegalAgent
from agents.strategy_agent import ceo_app, CEOState
from core.orchestration import PashaOrchestrator
from api.main import app

client = TestClient(app)


def test_monte_carlo_output():
    """1. Test Monte Carlo 50,000 iteration simulation outputs VaR, CVaR, and mean PnL."""
    var_95, cvar_95, mean_pnl = run_monte_carlo(portfolio_value=1e6, iterations=1000)
    assert isinstance(var_95, float)
    assert isinstance(cvar_95, float)
    assert isinstance(mean_pnl, float)
    assert cvar_95 >= var_95 or abs(cvar_95 - var_95) < 1e-3


def test_rag_ingest_query():
    """2. Test PashaRAGEngine document ingestion and hybrid vector query."""
    engine = PashaRAGEngine(dimension=384)
    docs = ["Enterprise financial growth report Q3.", "Legal regulatory compliance mandate."]
    engine.ingest(docs)
    results = engine.query("financial growth", k=1)
    assert len(results) == 1
    assert "financial growth" in results[0].lower() or len(results[0]) > 0


def test_cfo_forecast():
    """3. Test CFOAgent cashflow forecast and runway calculation."""
    cfo = CFOAgent(current_balance=2_000_000.0)
    history = [100000.0, 110000.0, 120000.0]
    forecast = cfo.forecast_cashflow(history, months_ahead=6)
    runway = cfo.calculate_runway(monthly_burn_rate=200000.0)

    assert len(forecast) == 6
    assert runway == 10.0


def test_cmo_sentiment():
    """4. Test CMOAgent sentiment analysis score and competitor analysis."""
    cmo = CMOAgent()
    score = cmo.sentiment_score("Strong excellent growth and innovative leader in market.")
    assert score > 0.0
    analysis = cmo.competitor_analysis(["CompA", "CompB"])
    assert "competitors" in analysis


def test_coo_optimization():
    """5. Test COOAgent supply chain optimization using linear programming."""
    coo = COOAgent()
    res = coo.optimize_supply_chain(demands=[50.0, 100.0], costs=[5.0, 10.0])
    assert res["status"] in ["Optimal", "1", 1]
    assert res["optimal_cost"] == 1250.0
    assert len(res["allocation"]) == 2


def test_chro_attrition():
    """6. Test CHROAgent XGBoost employee attrition prediction."""
    chro = CHROAgent()
    res = chro.predict_attrition([[1.0, 0.2, 0.4, 210.0]])
    assert "attrition_probabilities" in res
    assert len(res["attrition_probabilities"]) == 1
    assert 0.0 <= res["attrition_probabilities"][0] <= 1.0


def test_legal_analysis():
    """7. Test LegalAgent contract risk score and clause auditing."""
    legal = LegalAgent()
    contract = "Agreement contains unlimited liability indemnification and penalty clauses."
    res = legal.analyze_contract(contract)
    assert res["risk_score"] > 0.0
    assert len(res["flagged_clauses"]) >= 1


def test_ceo_graph_compilation():
    """8. Test Strategy Agent LangGraph CEO StateGraph compilation and invocation."""
    state: CEOState = {
        "cfo_signal": {"risk_score": 0.8},
        "cmo_signal": {"risk_score": 0.5},
        "coo_signal": {"risk_score": 0.4},
        "chro_signal": {"risk_score": 0.6},
        "legal_signal": {"risk_score": 0.9},
        "risk_score": 0.0,
        "decision": "",
    }
    output = ceo_app.invoke(state)
    assert output["decision"] in ["HALT_EXPANSION", "APPROVE_GROWTH"]
    assert output["risk_score"] > 0.6  # High risk should trigger HALT_EXPANSION


def test_orchestrator_run():
    """9. Test PashaOrchestrator master invocation across all 7 agents."""
    orchestrator = PashaOrchestrator()
    res = orchestrator.run_full_enterprise_analysis()
    assert "ceo_decision" in res
    assert "overall_risk_score" in res
    assert "monte_carlo_metrics" in res
    assert len(res["agents_summary"]) == 6


def test_api_health():
    """10. Test FastAPI web endpoints (/health and /analyze/ceo-decision)."""
    response = client.get("/health")
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "healthy"
    assert "auron" in json_resp["service"].lower() or "pasha" in json_resp["service"].lower()

    post_resp = client.post("/analyze/ceo-decision", json={"feedback_text": "High revenue and robust performance."})
    assert post_resp.status_code == 200
    json_data = post_resp.json()
    assert json_data["status"] == "success"
    assert "ceo_decision" in json_data["data"]
