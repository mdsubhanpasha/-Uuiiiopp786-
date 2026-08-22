# FinAgent-Ops: Autonomous Multi-Agent Financial Reconciliation & Fraud Detection Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-StateGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FinAgent-Ops** is an enterprise-grade, multi-agent autonomous framework implemented in Python, LangGraph, FastAPI, and Docker. It ingests ERP financial ledger transactions and bank statements, performs deterministic rule-matching and statistical Isolation Forest ML anomaly detection, runs forensic LLM tool-calling and Chain-of-Thought (CoT) audit evaluations, exports PDF/JSON audit artifacts, and automates GitHub commits and LinkedIn deployment publishing.

---

## 🏗️ Multi-Agent System Architecture

```text
                                  +-----------------------+
                                  |   Ledger & Bank CSVs  |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Ingestion Agent       |
                                  | Schema Validation     |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Reconciliation Agent  |
                                  | Deterministic + ML    |
                                  | (Isolation Forest)    |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Forensic Audit Agent  |
                                  | Tool Calling & CoT    |
                                  | Risk Level (L/M/H/C)  |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  | Report Agent          |
                                  | PDF & JSON Artifacts  |
                                  +-----------------------+
```

---

## 🤖 Implemented Multi-Agent Architecture

1. **Ingestion & Validation Agent (`src/agents/ingest_agent.py`)**: Validates transaction schemas, handles ERP/ledger reconciliation mismatches, and normalizes tabular data.
2. **Reconciliation & Anomaly Agent (`src/agents/recon_agent.py`)**: Executes deterministic rule-matching combined with statistical isolation forest algorithms to detect discrepancies.
3. **Forensic Audit LLM Agent (`src/agents/audit_agent.py`)**: Uses tool calling and chain-of-thought reflection to analyze flagged transactions, assign risk scores (Low/Medium/High/Critical), and generate root-cause explanations.
4. **Report & Notification Agent (`src/agents/report_agent.py`)**: Generates PDF audit reports (via FPDF2) and structured JSON artifacts.
5. **Supervisor Orchestrator (`src/graph_orchestrator.py`)**: LangGraph StateGraph managing inter-agent message routing and workflow state transitions.

---

## 📁 Repository Structure

```text
finagent-ops/
├── data/
│   ├── sample_ledger.csv      # Sample ERP financial ledger transactions
│   └── bank_statement.csv     # Sample bank statement transaction feed
├── src/
│   ├── __init__.py
│   ├── models.py              # Core Pydantic data models & LangGraph state
│   ├── graph_orchestrator.py  # LangGraph StateGraph orchestration graph
│   └── agents/
│       ├── __init__.py
│       ├── ingest_agent.py    # Schema validation & data normalization agent
│       ├── recon_agent.py     # Deterministic & ML Isolation Forest matching agent
│       ├── audit_agent.py     # LLM tool-calling & CoT forensic audit agent
│       └── report_agent.py    # FPDF PDF report & JSON artifact generation agent
├── scripts/
│   ├── github_deploy.py       # GitHub repository sync & release deployment script
│   └── linkedin_poster.py     # Automated technical announcement publisher
├── tests/
│   ├── test_agents.py         # Unit tests for multi-agent components
│   └── test_orchestrator.py   # Integration tests for LangGraph & FastAPI REST endpoints
├── Dockerfile                 # Multi-stage production container setup
├── .env.example               # Template environment configuration file
├── requirements.txt           # Python dependencies
├── README.md                  # Comprehensive system documentation
└── main.py                    # Application entry point (CLI & FastAPI server)
```

---

## 🚀 Quickstart & Usage

### 1. Installation
```bash
git clone https://github.com/your-username/finagent-ops.git
cd finagent-ops
pip install -r requirements.txt
```

### 2. Run CLI Reconciliation Workflow
Execute the end-to-end multi-agent pipeline from the command line:
```bash
python main.py --mode cli --ledger data/sample_ledger.csv --bank data/bank_statement.csv
```

### 3. Run FastAPI Web Service
Start the REST API server:
```bash
python main.py --mode api --port 8000
```

Access API Documentation:
- Swagger UI: `http://localhost:8000/docs`

### 4. Trigger Reconciliation via API
```bash
curl -X POST "http://localhost:8000/api/v1/reconcile" \
     -H "Content-Type: application/json" \
     -d '{"ledger_csv_path": "data/sample_ledger.csv", "bank_csv_path": "data/bank_statement.csv"}'
```

---

## 🐳 Docker Deployment

Build and run using Docker:
```bash
docker build -t finagent-ops:latest .
docker run -p 8000:8000 finagent-ops:latest
```

---

## 🧪 Testing & Code Quality

Run tests using `pytest`:
```bash
PYTHONPATH=. pytest tests/ -v
```

Check PEP8 compliance using `flake8`:
```bash
flake8 src scripts tests main.py
```

---

## 📄 License
Distributed under the MIT License.
