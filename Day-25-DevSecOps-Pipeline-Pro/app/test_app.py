"""
Unit tests for DevSecOps Flask application.
"""
import pytest
from app import app as flask_app


@pytest.fixture
def client():
    """Test client fixture."""
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as client:
        yield client


def test_home_endpoint(client):
    """Test root endpoint returns 200 and expected payload."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint returns status UP."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "UP"
    assert data["service"] == "devsecops-pipeline-pro"
