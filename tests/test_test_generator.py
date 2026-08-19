import pytest
import json
from unittest.mock import patch, MagicMock
from src.core.test_generator import generate_tests_for_codebase, TestGeneratorError

@patch('src.core.test_generator.genai')
def test_generate_tests_success(mock_genai):
    mock_model = MagicMock()
    mock_response = MagicMock()

    expected_result = {
        "predicted_coverage_percent": 85,
        "test_cases": [
            {"id": "TC-001", "title": "Test 1", "type": "Unit", "status": "Generated"}
        ],
        "test_scripts": [
            {"filename": "test_1.py", "content": "def test_1(): pass"}
        ],
        "test_data": [
            {"filename": "data.json", "content": '{"key": "value"}'}
        ]
    }

    mock_response.text = json.dumps(expected_result)
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    codebase = {"main.py": "def main(): pass"}
    result = generate_tests_for_codebase(codebase, api_key="dummy_key")

    assert result == expected_result
    mock_genai.configure.assert_called_once_with(api_key="dummy_key")

def test_generate_tests_missing_key():
    with patch.dict('os.environ', clear=True):
        with pytest.raises(TestGeneratorError, match="Gemini API key not provided"):
            generate_tests_for_codebase({"a.py": "code"})

@patch('src.core.test_generator.genai')
def test_generate_tests_invalid_json(mock_genai):
    mock_model = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "invalid json response"
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    with pytest.raises(TestGeneratorError, match="Failed to parse Gemini API response as JSON."):
        generate_tests_for_codebase({"a.py": "code"}, api_key="dummy")

@patch('src.core.test_generator.genai')
def test_generate_tests_missing_keys_in_response(mock_genai):
    mock_model = MagicMock()
    mock_response = MagicMock()

    # Missing test_scripts
    incomplete_result = {
        "predicted_coverage_percent": 85,
        "test_cases": [],
        "test_data": []
    }
    mock_response.text = json.dumps(incomplete_result)
    mock_model.generate_content.return_value = mock_response
    mock_genai.GenerativeModel.return_value = mock_model

    with pytest.raises(TestGeneratorError, match="Response JSON is missing required keys."):
        generate_tests_for_codebase({"a.py": "code"}, api_key="dummy")
