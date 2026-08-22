"""Unit and Integration Test Suite for CloudNative-Ops-Day3."""

from fastapi.testclient import TestClient
import pytest

from main import run_demo
from scripts.github_deploy import GitHubDeployer
from scripts.linkedin_poster import LinkedInPoster
from scripts.security_audit import SecurityAuditor
from src.app import app


@pytest.fixture
def client():
    """Fixture providing FastAPI TestClient instance."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint metadata response."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "devops-day3-cloudnative-pipeline"
    assert data["version"] == "1.0.0"
    assert data["status"] == "active"


def test_health_check_endpoint(client):
    """Test health check endpoint status and uptime."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "uptime_seconds" in data
    assert data["environment"] == "production"


def test_metrics_endpoint(client):
    """Test metrics endpoint operational data."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert data["system_status"] == "OPERATIONAL"
    assert "metrics" in data
    assert "total_requests" in data["metrics"]


def test_transaction_processing_success(client):
    """Test successful transaction processing via POST /transaction."""
    payload = {
        "transaction_id": "TX-10023",
        "account_id": "ACC-55412",
        "amount": 150.75,
        "currency": "USD",
        "transaction_type": "CREDIT",
    }
    response = client.post("/transaction", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["transaction_id"] == "TX-10023"
    assert data["amount"] == 150.75
    assert "reference_hash" in data


def test_transaction_processing_invalid_amount(client):
    """Test transaction processing with non-positive amount."""
    payload = {
        "transaction_id": "TX-INVALID",
        "account_id": "ACC-00000",
        "amount": -50.0,
        "currency": "USD",
    }
    response = client.post("/transaction", json=payload)
    assert response.status_code == 422  # Pydantic validation GT 0 constraint


def test_security_auditor():
    """Test automated security auditor for Dockerfile and requirements."""
    auditor = SecurityAuditor(
        dockerfile_path="Dockerfile",
        requirements_path="requirements.txt",
    )
    report = auditor.run_full_audit()
    assert report["audit_status"] == "PASSED"
    assert report["overall_compliance_score"] >= 80.0
    assert report["dependency_audit"]["vulnerabilities_found"] == 0


def test_github_deployer_dry_run():
    """Test GitHub deployer dry-run execution."""
    deployer = GitHubDeployer(repo_name="devops-day3-cloudnative-pipeline")
    status = deployer.check_git_status()
    assert "has_changes" in status

    res = deployer.sync_and_deploy(dry_run=True)
    assert res["status"] == "SUCCESS"
    assert res["target_repository"] == "devops-day3-cloudnative-pipeline"


def test_linkedin_poster_dry_run():
    """Test LinkedIn poster content generation and dry-run simulation."""
    poster = LinkedInPoster()
    content = poster.generate_post_content(
        repo_name="devops-day3-cloudnative-pipeline", security_score=100.0
    )
    assert "devops-day3-cloudnative-pipeline" in content
    assert "#DevOps" in content

    res = poster.publish_post(
        repo_name="devops-day3-cloudnative-pipeline",
        security_score=100.0,
        dry_run=True,
    )
    assert res["status"] == "SUCCESS"


def test_cli_demo_run():
    """Test main CLI demo runner function."""
    # Should run without raising exceptions
    run_demo()
