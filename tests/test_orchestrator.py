"""Integration tests for FinAgent-Ops LangGraph and FastAPI runner."""

from fastapi.testclient import TestClient

from main import app
from src.graph_orchestrator import FinAgentOrchestrator
from scripts.github_deploy import GitHubDeployer
from scripts.linkedin_poster import LinkedInPoster

client = TestClient(app)


def test_orchestrator_graph_execution():
    """Test full LangGraph orchestration graph execution."""
    orchestrator = FinAgentOrchestrator()
    final_state = orchestrator.run(
        ledger_path="data/sample_ledger.csv",
        bank_path="data/bank_statement.csv",
    )

    assert len(final_state["normalized_ledger"]) > 0
    assert len(final_state["normalized_bank"]) > 0
    assert len(final_state["discrepancies"]) > 0
    assert len(final_state["audit_results"]) > 0
    assert final_state["pdf_report_path"] is not None
    assert len(final_state["messages"]) >= 4


def test_fastapi_endpoints():
    """Test FastAPI REST API endpoints."""
    res_health = client.get("/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_rec = client.post(
        "/api/v1/reconcile",
        json={
            "ledger_csv_path": "data/sample_ledger.csv",
            "bank_csv_path": "data/bank_statement.csv",
        },
    )
    assert res_rec.status_code == 200
    body = res_rec.json()
    assert body["status"] == "success"
    assert "summary" in body
    assert body["discrepancy_count"] > 0

    res_gh = client.post(
        "/api/v1/deploy/github",
        json={"commit_message": "Test deploy", "dry_run": True},
    )
    assert res_gh.status_code == 200
    assert res_gh.json()["status"] == "success"

    res_li = client.post(
        "/api/v1/deploy/linkedin",
        json={"dry_run": True},
    )
    assert res_li.status_code == 200
    assert res_li.json()["status"] == "success"


def test_automation_scripts():
    """Test GitHub deployer and LinkedIn poster in dry run mode."""
    deployer = GitHubDeployer()
    status = deployer.check_git_status()
    assert "has_changes" in status

    dry_deploy = deployer.deploy(dry_run=True)
    assert dry_deploy["status"] == "success"

    poster = LinkedInPoster()
    post_text = poster.generate_post_content()
    assert "FinAgent-Ops" in post_text

    dry_post = poster.publish_post(dry_run=True)
    assert dry_post["status"] == "success"
