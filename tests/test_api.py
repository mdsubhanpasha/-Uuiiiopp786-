import sys
import os
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io
import zipfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.api.main import app, generated_tests_store

client = TestClient(app)

@pytest.fixture(autouse=True)
def clear_store():
    """Clear the in-memory store before each test."""
    generated_tests_store.clear()
    yield
    generated_tests_store.clear()

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "TestGen AI API is running."}

def test_ingest_no_input():
    response = client.post("/ingest_and_generate")
    assert response.status_code == 400
    assert "Must provide either a zip file or a GitHub URL" in response.json()["detail"]

@patch('src.api.main.ingest_github_repo')
@patch('src.api.main.generate_tests_for_codebase')
def test_ingest_github_success(mock_generate, mock_ingest):
    mock_ingest.return_value = {"main.py": "code"}
    mock_generate.return_value = {
        "predicted_coverage_percent": 90,
        "test_cases": [{"title": "TC1", "type": "Unit"}],
        "test_scripts": [{"filename": "test.py", "content": "pass"}],
        "test_data": []
    }

    response = client.post(
        "/ingest_and_generate",
        data={"github_url": "https://github.com/owner/repo", "gemini_key": "dummy"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "session_id" in data
    assert data["results"]["predicted_coverage_percent"] == 90

    session_id = data["session_id"]
    assert session_id in generated_tests_store

def test_export_scripts_not_found():
    response = client.get("/export/scripts/nonexistent")
    assert response.status_code == 404

def test_export_jira_not_found():
    response = client.get("/export/jira/nonexistent")
    assert response.status_code == 404

def test_export_jira_success():
    session_id = "test_session"
    generated_tests_store[session_id] = {
        "test_cases": [
            {"title": "Login Test", "type": "E2E"}
        ]
    }

    response = client.get(f"/export/jira/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert data["projects"][0]["suites"][0]["cases"][0]["title"] == "Login Test"
