# OmniRAG-Ops: Enterprise Multi-Tier Retrieval Engine

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code Style: PEP8](https://img.shields.io/badge/code%20style-PEP8-green.svg)](https://www.python.org/dev/peps/pep-0008/)

**OmniRAG-Ops** is an enterprise-grade, multi-architecture Retrieval-Augmented Generation (RAG) framework implemented in Python. It provides five distinct RAG paradigms, an intelligent dynamic query router, automated GitHub repository deployment scripts, and automated LinkedIn technical posting capabilities.

---

## 🏗️ Architectural Overview

```text
                                  +-----------------------+
                                  |   User Input Query    |
                                  +-----------+-----------+
                                              |
                                              v
                                  +-----------------------+
                                  |   RAG Query Router    |
                                  |    (src/router.py)    |
                                  +-----------+-----------+
                                              |
      +-------------------+-------------------+-------------------+-------------------+
      |                   |                   |                   |                   |
      v                   v                   v                   v                   v
+------------+     +------------+     +------------+     +------------+     +------------+
| Naive RAG  |     | Hybrid RAG |     | Graph RAG  |     |   CRAG     |     |Agentic RAG |
| (Dense)    |     |(BM25+Dense)|     |(NetworkX)  |     |(Web Fallback)|   |(LangGraph) |
+------------+     +------------+     +------------+     +------------+     +------------+
```

---

## 🚀 The 5 Implemented RAG Paradigms

### 1. Naive RAG (`src/naive_rag.py`)
- **Mechanism**: Standard dense vector embedding retrieval using cosine similarity.
- **Use Case**: Simple semantic lookups and direct factual queries.
- **Key Features**: In-memory vector store, document chunk indexing, cosine distance scoring.

### 2. Hybrid / Modular RAG (`src/hybrid_rag.py`)
- **Mechanism**: Combines BM25 lexical keyword search and dense vector search merged via **Reciprocal Rank Fusion (RRF)**.
- **Use Case**: Domain-specific queries containing technical jargon, exact model numbers, or acronyms.
- **Key Features**: BM25 Okapi search, RRF scoring ($K=60$), Cohere cross-encoder reranking simulation.

### 3. Graph RAG (`src/graph_rag.py`)
- **Mechanism**: Knowledge-graph-based multi-hop entity traversal using **NetworkX**.
- **Use Case**: Queries requiring structural reasoning across connected nodes, dependencies, and network topologies.
- **Key Features**: Dynamic entity extraction, directed multi-hop edge traversal, relation-aware context synthesis.

### 4. Corrective RAG - CRAG (`src/corrective_rag.py`)
- **Mechanism**: Evaluator-guided retrieval that assesses document confidence and triggers fallback web search when confidence drops below 0.65.
- **Use Case**: Fast-changing domains, real-time verification, or external information retrieval.
- **Key Features**: Confidence scoring evaluator, query re-writing module, dynamic web search integration (Tavily/Serper).

### 5. Agentic RAG (`src/agentic_rag.py`)
- **Mechanism**: Autonomous multi-turn reasoning graph inspired by **LangGraph**.
- **Use Case**: Complex multi-part enterprise requests requiring query decomposition and tool orchestration.
- **Key Features**: State machine (`AgentState`), tool suite (vector, graph, web search, code runner), reflection loop.

---

## 🚦 Intelligent RAG Router (`src/router.py`)

The `RAGRouter` automatically inspects incoming user queries and selects the optimal retrieval paradigm based on intent classification and complexity heuristics:

| Query Intent / Pattern | Target Paradigm | Primary Reasoning |
| :--- | :--- | :--- |
| Decompose / Multi-step / Workflow | **Agentic RAG** | Autonomous tool orchestration and reflection required |
| Relationships / Dependencies / Links | **Graph RAG** | Knowledge graph multi-hop traversal needed |
| Verify / Latest / Recent / Web | **Corrective RAG** | Evaluator check with web fallback |
| Specific terms / BM25 / RFC specs | **Hybrid RAG** | Lexical + Dense precision needed |
| Standard direct queries | **Naive RAG** | Direct vector similarity lookup |

---

## 📁 Repository Structure

```text
omnirag-ops/
├── data/
│   └── sample_corpus.json      # Enterprise knowledge base with entities & relations
├── src/
│   ├── __init__.py             # Package exports
│   ├── naive_rag.py            # Naive Dense Vector RAG
│   ├── hybrid_rag.py           # Hybrid BM25 + Vector RAG with RRF & Reranker
│   ├── graph_rag.py            # Knowledge Graph Multi-Hop RAG
│   ├── corrective_rag.py       # Corrective RAG with Web Search Fallback
│   ├── agentic_rag.py          # Multi-Turn Agentic RAG with Reflection
│   └── router.py               # Dynamic Query Router & Benchmarking
├── scripts/
│   ├── github_deploy.py        # GitHub repository deployment script
│   └── linkedin_poster.py      # Automated technical post generator
├── tests/                      # Pytest suite
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
└── main.py                     # CLI & Interactive Demo runner
```

---

## 🛠️ Installation & Quickstart

1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-username/omnirag-ops.git
   cd omnirag-ops
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   ```bash
   cp .env.example .env
   ```

4. **Run interactive demo mode**:
   ```bash
   python main.py --mode demo
   ```

5. **Run query with automatic dynamic routing**:
   ```bash
   python main.py --query "How is Istio related to Zero Trust and Kubernetes?" --mode auto
   ```

6. **Benchmark all 5 paradigms on a single query**:
   ```bash
   python main.py --query "Decompose security compliance requirements" --mode benchmark
   ```

---

## 🤖 Automation Scripts

### 1. GitHub Repository Deployer (`scripts/github_deploy.py`)
Automates pushing code changes and repository initialization to GitHub via PyGithub or Git CLI:
```bash
python scripts/github_deploy.py --commit-msg "Deploy enterprise OmniRAG-Ops release"
```

### 2. LinkedIn Automated Poster (`scripts/linkedin_poster.py`)
Generates structured technical post announcements showcasing the OmniRAG-Ops architecture and publishes via LinkedIn API:
```bash
python scripts/linkedin_poster.py --publish
```

---

## 🧪 Testing & Code Quality

Run tests using `pytest`:
```bash
pytest tests/ -v
```

Check code formatting and PEP8 compliance using `flake8`:
```bash
flake8 src/ scripts/ tests/ main.py
```

---

## 📄 License
Distributed under the MIT License.
