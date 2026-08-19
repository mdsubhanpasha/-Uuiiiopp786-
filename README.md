# TestGen AI - Enterprise QA Automation Tool 🤖

![Used by Enterprises](https://img.shields.io/badge/Used%20by-Enterprises-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-009688?logo=fastapi)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31-FF4B4B?logo=streamlit)
![Gemini](https://img.shields.io/badge/Gemini-2.0%20Pro-4285F4?logo=google)

An AI-powered SaaS that reads any codebase and automatically generates 200+ test cases + Playwright/Python automation scripts in minutes.

## 🌟 Why Enterprises Need This

In modern enterprise software development, testing is often the bottleneck. Manual test creation is slow, error-prone, and struggles to keep up with rapid release cycles.

**TestGen AI solves this by:**
- **Accelerating Time-to-Market:** Generate comprehensive test suites in minutes, not weeks.
- **Improving Test Coverage:** AI identifies edge cases and integration points that human testers might miss.
- **Reducing QA Costs:** Automate the repetitive task of writing boilerplate test code and generating sample data.
- **Seamless Integration:** Exports directly to standard formats for Jira and TestRail, and provides executable scripts ready for your CI/CD pipeline.

## ✨ Core Features

1. **Codebase Ingestion**: Upload a `.zip` file or connect to a public GitHub repository URL.
2. **AI Test Case Generation**: Uses Gemini 2.0 Pro to deeply analyze the codebase. Generates test cases covering Unit Tests, Integration Tests, Edge Cases, and E2E User Flows.
3. **Auto Code Generation**: Auto-generates executable Playwright/Python test scripts with assertions for the identified test cases.
4. **Test Data Generation**: Creates sample CSV/JSON test data for boundary values, negative cases, and invalid inputs.
5. **Coverage Prediction**: Displays "Predicted Code Coverage %" before running tests based on the generated cases.
6. **Enterprise Dashboard**:
    - Track "Bugs Prevented" and "Time Saved".
    - Download test cases as CSV.
    - Export test scripts and data as a `.zip` archive.
    - Export to Jira/TestRail JSON format.

## 🏗️ Architecture

- **Backend**: FastAPI, Python, Gemini 2.0 Pro API, PyGithub
- **Frontend**: Streamlit with a custom Datadog-inspired dark theme for a professional B2B SaaS look.
- **Infrastructure**: Dockerfile + docker-compose.yml for 1-click deployment.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose (recommended)
- OR Python 3.10+
- Google Gemini API Key
- (Optional) GitHub Personal Access Token for higher rate limits

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd CodeGuard-AI-Enterprise
   ```

2. **Configure Environment:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Run with Docker:**
   ```bash
   docker-compose up --build
   ```
   The UI will be available at `http://localhost:8501` and the API at `http://localhost:8000`.

### Local Development Setup

```bash
# Create virtual env
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Run API (in one terminal)
uvicorn src.api.main:app --reload

# Run UI (in another terminal)
streamlit run src/ui/app.py
```
