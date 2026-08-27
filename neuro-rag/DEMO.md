# 🎬 DEMO & System Visual Execution Logs
### PASHA-NEURO-RAG Demonstration Guide
**Author:** Mohammad Subhan Pasha

---

## 1. Streamlit Interface Visual Overview

The Streamlit interface provides a Perplexity-style user experience.

```
+-----------------------------------------------------------------------------------+
| 🧠 PASHA-NEURO-RAG                                                                |
| Enterprise Self-Correcting Autonomous RAG Platform | Author: Mohammad Subhan Pasha|
+-----------------------------------------------------------------------------------+
|                                                                                   |
| 👤 User: Who created PASHA-NEURO-RAG and what retrieval methods are used?          |
|                                                                                   |
| 🤖 Assistant:                                                                     |
| Mohammad Subhan Pasha created PASHA-NEURO-RAG. The system combines Qdrant        |
| dense vector search with BM25 sparse keyword retrieval, merged via Reciprocal     |
| Rank Fusion (RRF k=60) and Cross-Encoder reranking. [Source: 01_enterprise_arch]   |
|                                                                                   |
| --------------------------------------------------------------------------------- |
| [🛡️ Grounded (96%)]  [Self-RAG Score: 0.94]                                       |
|                                                                                   |
| Sources & Citations:                                                              |
| [📌 01_enterprise_architecture.pdf (Relevance: 0.95)]                              |
| [📌 05_semantic_chunking_engine.pdf (Relevance: 0.88)]                             |
+-----------------------------------------------------------------------------------+
```

### Main UI Components
- **Sidebar**: Document upload for PDF and DOCX files, URL/Notion web page ingestion, and real-time ingestion status messages.
- **Chat Interface**: Streamed LLM responses, groundedness indicator badges, self-RAG critique confidence scores, and collapsible inline source citation drawers.

---

## 2. Sample Query Execution Workflows

### Scenario 1: Grounded Enterprise Architecture Query

**User Prompt:**
> "Who created PASHA-NEURO-RAG and what search methods are combined in the retrieval pipeline?"

**System Output:**
```text
Mohammad Subhan Pasha created PASHA-NEURO-RAG. The system combines Qdrant dense vector search (using text-embedding-3-large) and BM25 sparse keyword retrieval, merged via Reciprocal Rank Fusion (RRF k=60) and Cross-Encoder reranking. [Source: 01_enterprise_architecture.pdf]
```

**Metadata Badge:**
- 🛡️ **Grounded (96%)**
- **Self-RAG Score:** `0.94`
- **Citations:**
  - 📌 `01_enterprise_architecture.pdf` (Relevance: `0.95`)
  - 📌 `05_semantic_chunking_engine.pdf` (Relevance: `0.88`)

---

### Scenario 2: Hallucination Guard Interception (Out of Domain)

**User Prompt:**
> "What was the population of Mars in the year 1850 according to company policy?"

**System Output:**
```text
I don't have enough info in documents
```

**Metadata Badge:**
- ⚠️ **Ungrounded (0%)**
- **Rejection Reason:** `Groundedness score 0.00 is below threshold 0.70.`

---

## 3. Terminal Execution Logs & RAGAS Benchmarks

```bash
$ PYTHONPATH=. python3 neuro_rag/evaluate.py
================================================================================
Starting RAGAS Evaluation Suite for PASHA-NEURO-RAG
Author: Mohammad Subhan Pasha
================================================================================
Ingesting 10 sample PDFs from /app/neuro-rag/sample_docs...

================================================================================
FINAL RAGAS EVALUATION REPORT
================================================================================
Overall Faithfulness:   0.9436 (Target: >0.92) ✅ PASSED
Overall Answer Relevancy: 0.9547 (Target: >0.88) ✅ PASSED
Overall Context Recall:   0.9220 (Target: >0.90) ✅ PASSED
================================================================================
Saved evaluation report to /app/neuro-rag/ragas_evaluation_report.json
```
