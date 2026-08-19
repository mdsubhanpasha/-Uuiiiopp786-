import os
import json
from typing import Dict, Any, Optional

import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError

class TestGeneratorError(Exception):
    """Exception raised for errors in the Test Generator."""
    pass

def generate_tests_for_codebase(codebase_files: Dict[str, str], api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyzes a codebase and generates test cases, scripts, data, and coverage prediction using Gemini.

    Args:
        codebase_files (Dict[str, str]): A dictionary mapping file paths to their string contents.
        api_key (Optional[str]): The Gemini API key.

    Returns:
        Dict[str, Any]: A dictionary containing the generated testing assets.
    """
    key = api_key or os.environ.get("GEMINI_API_KEY")
    if not key:
        raise TestGeneratorError("Gemini API key not provided or found in environment variables.")

    genai.configure(api_key=key)

    import ast

    try:
        # Use gemini-1.5-pro for larger context and better reasoning
        model = genai.GenerativeModel('gemini-1.5-pro')
    except Exception as e:
        raise TestGeneratorError(f"Failed to initialize model: {e}")

    # Prepare the codebase string for the prompt with AST parsing for Python files
    codebase_summary = ""
    for path, content in codebase_files.items():
        if path.endswith('.py'):
            try:
                tree = ast.parse(content)
                summary = []
                for node in tree.body:
                    if isinstance(node, ast.FunctionDef):
                        summary.append(f"Function: {node.name}(...)")
                    elif isinstance(node, ast.ClassDef):
                        summary.append(f"Class: {node.name}")
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                summary.append(f"  Method: {item.name}(...)")
                truncated_content = "\\n".join(summary) if summary else "No classes or functions found."
            except SyntaxError:
                truncated_content = content[:1000] + "\n...[truncated]" if len(content) > 1000 else content
        else:
            truncated_content = content[:1000] + "\n...[truncated]" if len(content) > 1000 else content

        codebase_summary += f"\n--- File: {path} ---\n{truncated_content}\n"

    prompt = f"""
    You are an expert Staff QA Automation Engineer. Analyze the following codebase and automatically generate a comprehensive test suite.

    Codebase:
    {codebase_summary}

    Generate the output strictly as a JSON object with the following structure:
    {{
        "predicted_coverage_percent": <int 0-100>,
        "test_cases": [
            {{
                "id": "TC-001",
                "title": "<Test case title>",
                "type": "<Unit | Integration | Edge Case | E2E>",
                "status": "Generated"
            }}
        ],
        "test_scripts": [
            {{
                "filename": "<e.g., test_login.py or test_login.spec.ts>",
                "content": "<Executable Playwright/Python test script with assertions>"
            }}
        ],
        "test_data": [
            {{
                "filename": "<e.g., users.csv or config.json>",
                "content": "<Sample test data for boundary values, negative cases, invalid inputs>"
            }}
        ]
    }}

    Ensure you generate diverse test types including Unit Tests, Integration Tests, Edge Cases, and E2E User Flows.
    For the scripts, provide the actual code.
    For the test data, provide the raw content (CSV or JSON string).
    """

    try:
        response = model.generate_content(prompt)
        text_response = response.text.strip()

        if text_response.startswith("```json"):
            text_response = text_response[7:-3].strip()
        elif text_response.startswith("```"):
            text_response = text_response[3:-3].strip()

        result = json.loads(text_response)

        required_keys = ["predicted_coverage_percent", "test_cases", "test_scripts", "test_data"]
        if not all(key in result for key in required_keys):
             raise TestGeneratorError("Response JSON is missing required keys.")

        return result
    except json.JSONDecodeError:
        raise TestGeneratorError("Failed to parse Gemini API response as JSON.")
    except GoogleAPIError as e:
         raise TestGeneratorError(f"Gemini API request failed: {e}")
    except Exception as e:
        raise TestGeneratorError(f"An unexpected error occurred during generation: {e}")
