"""Comprehensive Unit and Integration Tests for PASHA-OS V2 - Enterprise 20-Agent MNC OS."""

import os
from fastapi.testclient import TestClient

from agents.base_agent import BaseAgent
from agents.strategy_agent import CEOAgent
from agents.cfo_agent import CFOAgent
from agents.cto_agent import CTOAgent
from agents.cmo_agent import CMOAgent
from agents.coo_agent import COOAgent
from agents.chro_agent import CHROAgent
from agents.legal_agent import LegalAgent, CLOAgent
from agents.staff_engineer_agent import StaffEngineerAgent
from agents.qa_agent import QAAgent
from agents.devops_agent import DevOpsAgent
from agents.security_agent import SecurityAgent
from agents.data_scientist_agent import DataScientistAgent
from agents.ml_engineer_agent import MLEngineerAgent
from agents.analytics_agent import AnalyticsAgent
from agents.research_agent import ResearchAgent
from agents.product_manager_agent import ProductManagerAgent
from agents.ux_research_agent import UXResearchAgent
from agents.growth_hacker_agent import GrowthHackerAgent
from agents.sales_agent import SalesAgent, SalesStrategistAgent
from agents.customer_success_agent import CustomerSuccessAgent
from agents.validator_agent import ValidatorAgent
from agents.critic_agent import CriticAgent

from core.meeting_orchestrator import MeetingOrchestrator
from core.orchestration import PashaOrchestrator
from api.main import app

client = TestClient(app)


def test_base_agent_research_and_format():
    """Test BaseAgent research_tool and format_decision ReAct structure."""
    agent = BaseAgent("TestAgent", "Testing", "TEST_DIVISION")
    res = agent.research_tool("Enterprise AI Agent OS benchmarks 2025")
    assert "query" in res
    assert "summary" in res
    assert len(res["search_results"]) >= 1

    dec = agent.format_decision(
        reasoning="Step by step reasoning chain",
        data_sources=["DataFeed1"],
        alternatives_considered=["Option A", "Option B"],
        final_decision="Option A",
        confidence_score=0.95,
    )
    assert dec["agent_name"] == "TestAgent"
    assert dec["division"] == "TEST_DIVISION"
    assert dec["confidence_score"] == 0.95
    assert dec["reasoning"] == "Step by step reasoning chain"


def test_cfo_decimal_calculations():
    """Test CFOAgent Decimal precision, P&L, unit economics, and cashflow."""
    cfo = CFOAgent(current_balance="5000000.00")
    forecast = cfo.forecast_cashflow([100000.0, 110000.0, 120000.0], months_ahead=6)
    assert len(forecast) == 6

    runway = cfo.calculate_runway("250000.00")
    assert runway == 20.0

    unit_econ = cfo.calculate_unit_economics(cac="150.00", ltv="900.00", arpu="50.00", cogs="10.00")
    assert unit_econ["ltv_cac_ratio"] == 6.0
    assert unit_econ["gross_margin_percent"] == 80.0
    assert unit_econ["healthy_unit_economics"] is True

    p_and_l = cfo.generate_p_and_l(revenue="1000000.00", opex="400000.00", cogs="200000.00")
    assert p_and_l["gross_profit_usd"] == 800000.0
    assert p_and_l["net_income_usd"] == 400000.0
    assert p_and_l["net_margin_percent"] == 40.0

    risk_rep = cfo.risk_assessment()
    assert risk_rep["confidence_score"] == 0.999
    assert "reasoning" in risk_rep


def test_cto_agent():
    """Test CTOAgent tech stack evaluation and code review."""
    cto = CTOAgent()
    eval_res = cto.evaluate_tech_stack({"qps": 15000, "latency_sla_ms": 20})
    assert "tech_stack" in eval_res
    assert "backend_framework" in eval_res["tech_stack"]

    review_res = cto.review_code_quality(["src/api/main.py"])
    assert review_res["flake8_compliance"] is True


def test_cmo_agent():
    """Test CMOAgent GTM strategy, campaign ROI, and sentiment analysis."""
    cmo = CMOAgent()
    assert cmo.sentiment_score("Outstanding market response and profits") > 0.0
    assert cmo.sentiment_score("Decline and churn loss") < 0.0
    assert cmo.sentiment_score("") == 0.0

    gtm_res = cmo.analyze_gtm_and_campaign(budget_usd=100000.0)
    assert gtm_res["projected_leads"] == 1250
    assert "competitors" in cmo.competitor_analysis()


def test_coo_agent():
    """Test COOAgent PuLP supply chain LP optimization."""
    coo = COOAgent()
    res = coo.optimize_supply_chain(demands=[100.0, 200.0], costs=[10.0, 15.0])
    assert res["status"] == "Optimal"
    assert res["optimal_cost"] == 4000.0


def test_chro_agent():
    """Test CHROAgent XGBoost turnover prediction."""
    chro = CHROAgent()
    res = chro.predict_attrition([[1.0, 0.2, 0.4, 210.0]])
    assert "attrition_probabilities" in res
    assert len(res["attrition_probabilities"]) == 1


def test_legal_and_clo_agent():
    """Test LegalAgent / CLOAgent contract auditing."""
    legal = LegalAgent()
    res = legal.analyze_contract("This contract includes unlimited liability indemnification offshore penalty clauses.")
    assert res["risk_score"] > 0.0
    assert res["compliance_status"] == "NON_COMPLIANT"

    clo = CLOAgent()
    assert clo.agent_name == "CLO / Legal Agent"


def test_engineering_division_agents():
    """Test StaffEngineer, QA, DevOps, and Security agents."""
    staff = StaffEngineerAgent()
    s_res = staff.design_architecture_and_code("auth_service")
    assert "AuthService" in s_res["generated_code"]

    qa = QAAgent()
    q_res = qa.generate_and_audit_tests("core.rag_engine")
    assert q_res["coverage_target"] == 100.0

    devops = DevOpsAgent()
    d_res = devops.audit_infrastructure_and_healing(
        {"active_pods": 10, "cpu_utilization_percent": 90.0, "crash_loops": 1}
    )
    assert d_res["healing_action"] == "SCALE_UP_PODS_AND_RESTART_FAILED"

    sec = SecurityAgent()
    sec_res = sec.scan_vulnerabilities("SELECT * FROM users WHERE input = ' OR '1'='1'")
    assert sec_res["final_decision"]["security_status"] == "VULNERABILITY_FOUND"


def test_data_and_ai_division_agents():
    """Test DataScientist, MLEngineer, Analytics, and Research agents."""
    ds = DataScientistAgent()
    ds_res = ds.train_and_track_model("RandomForest Classifier")
    assert ds_res["model_metrics"]["accuracy"] > 0.9

    mle = MLEngineerAgent()
    mle_res = mle.deploy_and_monitor_model("model_v1")
    assert mle_res["deployment_metrics"]["throughput_qps"] == 2500

    analytics = AnalyticsAgent()
    ana_res = analytics.track_kpis_and_bi("Q3_2025")
    assert ana_res["kpis"]["net_revenue_retention_percent"] == 124.5

    research = ResearchAgent()
    r_res = research.execute_deep_research("Enterprise AI Agent MNC OS")
    assert "primary_research" in r_res


def test_product_growth_customer_sales_agents():
    """Test ProductManager, UXResearch, GrowthHacker, Sales, and CustomerSuccess agents."""
    pm = ProductManagerAgent()
    pm_res = pm.prioritize_roadmap_rice()
    assert len(pm_res["prioritized_backlog"]) == 3

    ux = UXResearchAgent()
    ux_res = ux.analyze_ab_test_and_feedback(
        variant_a_conversions=400, variant_b_conversions=500, total_visitors=5000
    )
    assert ux_res["final_decision"]["winning_variant"] == "VARIANT_B"

    growth = GrowthHackerAgent()
    g_res = growth.analyze_growth_funnel()
    assert g_res["viral_k_factor"] == 1.25

    sales = SalesAgent()
    s_res = sales.score_lead_and_playbook({
        "company_name": "Acme",
        "employee_count": 5000,
        "budget_approved": True,
        "decision_maker_engaged": True,
    })
    assert s_res["lead_score"] == 100.0

    sales_strat = SalesStrategistAgent()
    assert sales_strat.agent_name == "Sales Strategist Agent"

    cs = CustomerSuccessAgent()
    cs_res = cs.predict_churn_and_health({
        "account_name": "ClientA",
        "weekly_logins": 2,
        "open_critical_tickets": 3,
        "nps_score": 4,
    })
    assert cs_res["health_status"] == "AT_RISK"


def test_quality_assurance_agents():
    """Test ValidatorAgent and CriticAgent."""
    validator = ValidatorAgent()
    sample_output = {
        "reasoning": "Sufficient reasoning chain provided here.",
        "data_sources": ["Telemetry"],
        "alternatives_considered": ["Alt1"],
        "final_decision": "Approved",
        "confidence_score": 0.95,
    }
    v_res = validator.validate_agent_output("TestAgent", sample_output)
    assert v_res["is_valid"] is True

    invalid_output = {"confidence_score": 0.2}
    v_invalid = validator.validate_agent_output("TestAgent", invalid_output)
    assert v_invalid["is_valid"] is False

    critic = CriticAgent()
    c_res = critic.red_team_decision("TestAgent", {"confidence_score": 0.99, "risk_score": 0.8, "reasoning": "Short"})
    assert "flaws_found" in c_res


def test_ceo_agent_and_okrs():
    """Test CEOAgent vision and OKR formulation."""
    ceo = CEOAgent()
    res = ceo.formulate_vision_and_okrs({"industry": "Enterprise SaaS"})
    assert len(res["okrs"]) == 2


def test_meeting_orchestrator_execution():
    """Test MeetingOrchestrator Daily Standup, Weekly Department, and Monthly Board meetings."""
    mo = MeetingOrchestrator(artifacts_dir="artifacts/test_meetings")
    standup = mo.run_daily_standup()
    assert standup["meeting_type"] == "DAILY_STANDUP"
    assert os.path.exists(standup["transcript_file"])

    weekly_eng = mo.run_weekly_department_meeting("ENGINEERING DIVISION")
    assert weekly_eng["meeting_type"] == "WEEKLY_DEPARTMENT_MEETING"

    weekly_data = mo.run_weekly_department_meeting("DATA & AI DIVISION")
    assert weekly_data["meeting_type"] == "WEEKLY_DEPARTMENT_MEETING"

    weekly_prod = mo.run_weekly_department_meeting("PRODUCT & GROWTH DIVISION")
    assert weekly_prod["meeting_type"] == "WEEKLY_DEPARTMENT_MEETING"

    weekly_cust = mo.run_weekly_department_meeting("CUSTOMER & SALES DIVISION")
    assert weekly_cust["meeting_type"] == "WEEKLY_DEPARTMENT_MEETING"

    board = mo.run_monthly_board_meeting()
    assert board["meeting_type"] == "MONTHLY_BOARD_MEETING"
    assert "quality_control" in board


def test_master_orchestrator_20_agents():
    """Test PashaOrchestrator aggregated 20-agent MNC analysis."""
    orchestrator = PashaOrchestrator()
    res = orchestrator.run_full_enterprise_analysis()
    assert "ceo_decision" in res
    assert "divisions_summary" in res
    assert "CORE_C_SUITE" in res["divisions_summary"]
    assert "ENGINEERING_DIVISION" in res["divisions_summary"]
    assert "DATA_AND_AI_DIVISION" in res["divisions_summary"]
    assert "PRODUCT_AND_GROWTH_DIVISION" in res["divisions_summary"]
    assert "CUSTOMER_AND_SALES_DIVISION" in res["divisions_summary"]


def test_api_endpoints_v2():
    """Test FastAPI REST endpoints and WebSocket streams for 20-agent system."""
    health_resp = client.get("/health")
    assert health_resp.status_code == 200
    assert health_resp.json()["agents_active"] == 20

    metrics_resp = client.get("/metrics")
    assert metrics_resp.status_code == 200

    cfo_resp = client.post("/agents/cfo", json={"historical_cashflows": [100000.0, 110000.0], "burn_rate": 200000.0})
    assert cfo_resp.status_code == 200
    assert "unit_economics" in cfo_resp.json()["data"]

    cmo_resp = client.post("/agents/cmo", json={"text": "Strong growth", "competitors": ["Comp1"]})
    assert cmo_resp.status_code == 200

    research_resp = client.post("/research", json={"query": "Enterprise AI OS", "topic": "Tech"})
    assert research_resp.status_code == 200

    meeting_resp = client.post("/meetings/run", json={"meeting_type": "DAILY_STANDUP"})
    assert meeting_resp.status_code == 200

    weekly_resp = client.post(
        "/meetings/run", json={"meeting_type": "WEEKLY_DEPARTMENT", "department": "ENGINEERING DIVISION"}
    )
    assert weekly_resp.status_code == 200

    board_resp = client.post("/meetings/run", json={"meeting_type": "MONTHLY_BOARD"})
    assert board_resp.status_code == 200

    with client.websocket_connect("/board/meeting") as ws:
        msg1 = ws.receive_json()
        assert msg1["event"] == "MEETING_STARTED"
