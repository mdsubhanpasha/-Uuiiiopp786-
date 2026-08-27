"""
Unit and Integration Tests for AUTO-GROWTH Autonomous AI Marketing Agency.
Tests all 5 agents, autonomous workflow execution, output artifact creation, and FastAPI REST endpoints.
"""

import os
import sys

# Setup path for imports
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

from mock_db.analytics_db import MockAnalyticsDB  # noqa: E402
from agents.market_research_agent import MarketResearchAgent  # noqa: E402
from agents.content_agent import ContentAgent  # noqa: E402
from agents.seo_agent import SEOAgent  # noqa: E402
from agents.ad_agent import AdAgent  # noqa: E402
from agents.analytics_agent import AnalyticsAgent  # noqa: E402
from workflow import AutonomousMarketingWorkflow  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from api.main import app  # noqa: E402


def test_mock_analytics_db():
    db = MockAnalyticsDB()
    benchmarks = db.get_industry_benchmarks("Enterprise_AI")
    assert "avg_cpc" in benchmarks
    assert "conversion_rate" in benchmarks
    serp = db.get_serp_data("autonomous ai agents")
    assert len(serp) > 0


def test_market_research_agent():
    agent = MarketResearchAgent()
    res = agent.research("PASHA-OS", "US startups")
    assert res["product_name"] == "PASHA-OS"
    assert len(res["top_competitors"]) == 3
    assert len(res["target_buyer_personas"]) == 2


def test_content_agent():
    agent = ContentAgent()
    res = agent.generate_campaign_content("PASHA-OS", "US startups", {})
    assert len(res["blogs"]) == 5
    assert len(res["linkedin_posts"]) == 10
    assert len(res["tweets"]) == 3


def test_seo_agent():
    agent = SEOAgent()
    content_agent = ContentAgent()
    content_data = content_agent.generate_campaign_content("PASHA-OS", "US startups", {})
    res = agent.optimize_campaign_seo("PASHA-OS", "US startups", content_data)
    assert res["campaign_avg_seo_score"] > 0
    assert len(res["blog_seo_reports"]) == 5


def test_ad_agent():
    agent = AdAgent()
    res = agent.generate_ad_campaign("PASHA-OS", "US startups", 1000.0)
    assert len(res["ad_copies"]["search_ads"]) == 2
    assert len(res["ad_copies"]["display_ads"]) == 2
    assert res["budget_allocation"]["total_estimated_clicks"] > 0


def test_analytics_agent():
    analytics_agent = AnalyticsAgent()
    ad_agent = AdAgent()
    ad_data = ad_agent.generate_ad_campaign("PASHA-OS", "US startups", 1000.0)
    res = analytics_agent.analyze_and_project_roi("PASHA-OS", "US startups", 1000.0, ad_data)
    fin = res["financial_summary"]
    assert fin["total_investment"] == 1000.0
    assert fin["projected_gross_revenue"] > 0
    assert fin["roi_percentage"] > 0


def test_autonomous_workflow_and_outputs(tmp_path):
    output_dir = str(tmp_path / "outputs")
    workflow = AutonomousMarketingWorkflow(output_dir=output_dir)
    results = workflow.run_campaign(product_name="PASHA-OS", target_audience="US startups", budget=1000.0)

    assert results["product_name"] == "PASHA-OS"
    assert results["content"]["blog_count"] == 5
    assert results["content"]["linkedin_count"] == 10

    # Verify generated output files
    assert os.path.exists(os.path.join(output_dir, "campaign_summary.json"))
    assert os.path.exists(os.path.join(output_dir, "linkedin_posts.md"))
    assert os.path.exists(os.path.join(output_dir, "ad_campaign_strategy.md"))
    assert os.path.exists(os.path.join(output_dir, "roi_and_growth_strategy.md"))

    blogs_dir = os.path.join(output_dir, "blogs")
    assert os.path.exists(blogs_dir)
    assert len(os.listdir(blogs_dir)) == 5


def test_fastapi_endpoints():
    client = TestClient(app)

    # Health check
    response = client.get("/api/v1/campaign/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

    # Latest campaign endpoint
    response = client.get("/api/v1/campaign/latest")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Run campaign endpoint
    payload = {"product_name": "PASHA-OS", "target_audience": "US startups", "budget": 1000.0}
    response = client.post("/api/v1/campaign/run", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
