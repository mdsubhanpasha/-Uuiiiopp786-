# PASHA-OS: Predictive Autonomous System for Holistic Administration

[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.0-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.39-orange.svg)](https://github.com/langchain-ai/langgraph)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39.0-red.svg)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**PASHA-OS** (Predictive Autonomous System for Holistic Administration) is an enterprise-grade Autonomous CEO Enterprise Intelligence OS designed to assist C-Suite executives with real-time risk assessment, financial runway forecasting, legal contract audit, supply chain optimization, employee turnover prediction, and corporate strategy decision-making.

---

## 🏗️ Multi-Agent Architecture & Flow

```mermaid
graph TD
    A[Enterprise Data Feed] --> B[PashaOrchestrator]
    B --> C[CFO Agent: Cashflow & Runway]
    B --> D[CMO Agent: Sentiment & Competitor Threat]
    B --> E[COO Agent: Linear Supply Optimization]
    B --> F[CHRO Agent: XGBoost Attrition Model]
    B --> G[Legal Agent: 10 Statutory Audit Rules]
    B --> H[Investor Agent: ARR & Valuation Synthesis]

    C --> I[LangGraph CEO StateGraph]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J{Board Decision Node}
    J -->|Aggregated Risk > 0.7| K[HALT_EXPANSION]
    J -->|Aggregated Risk <= 0.7| L[APPROVE_GROWTH]

    K --> M[Streamlit CEO Command Center & REST API]
    L --> M
```

---

## 🤖 C-Suite Autonomous Agents

| Agent | Class | Core Responsibility | Technique / Library |
|---|---|---|---|
| **CFO Agent** | `CFOAgent` | Cashflow forecasting, liquidity runway, financial risk assessment | NumPy, Linear Trend Analysis |
| **CMO Agent** | `CMOAgent` | Market sentiment scoring, competitor intelligence threat matrix | NLP Lexicon Analysis |
| **COO Agent** | `COOAgent` | Global supply chain distribution & cost minimization | PuLP Linear Programming |
| **CHRO Agent**| `CHROAgent`| Workforce turnover and high-risk attrition prediction | XGBoost Machine Learning |
| **Legal Agent**| `LegalAgent`| Regulatory statutory rule auditing and contract risk assessment | Statutory Rule Engine (10 Rules) |
| **Investor Agent**| `InvestorAgent`| Investor relations, ARR tracking, valuation multiple synthesis | Enterprise Financial Modeling |
| **Strategy CEO Agent**| `ceo_app` | Executive decision synthesis (HALT_EXPANSION / APPROVE_GROWTH) | LangGraph StateGraph |

---

## 🛠️ Tech Stack

* **Core AI & Workflow Orchestration**: LangGraph (0.2.39), LangChain (0.3.7), FAISS (1.8.0), ChromaDB (0.5.18)
* **API & Real-time WebSockets**: FastAPI (0.115.0), Uvicorn, WebSockets, Prometheus Client
* **Dashboard & Visualizations**: Streamlit (1.39.0), Plotly (5.24.1), FPDF2, python-pptx
* **Analytics & Optimization**: Prophet, XGBoost, scikit-learn, PuLP, NumPy
* **Testing & Quality Assurance**: Pytest (8.3.2), Flake8 (7.1.0)

---

## 🚀 Quick Start

### 1. Local Setup
```bash
git clone https://github.com/your-org/PASHA-OS.git
cd PASHA-OS
pip install -r requirements.txt
```

### 2. Run FastAPI Web Service
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```
* Interactive Swagger Docs: `http://localhost:8000/docs`
* Prometheus Telemetry: `http://localhost:8000/metrics`

### 3. Launch Streamlit Executive Command Center
```bash
streamlit run dashboard/app.py
```
* Access Dashboard: `http://localhost:8501`

---

## 🐳 Docker Deployment

Run all services (FastAPI, Streamlit Dashboard, Prometheus) with Docker Compose:

```bash
docker-compose up --build
```

---

## 🧪 Testing & Code Quality

Run full unit and integration test suite:
```bash
python3 -m pytest tests/ -v
```

Run PEP8 compliance check:
```bash
flake8 . --max-line-length=120
```

---

## 📄 License
Distributed under the MIT License.
