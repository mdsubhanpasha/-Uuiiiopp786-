"""Intelligent RAG Query Router implementation.

Analyzes query semantics, structure, and intent to dynamically route requests
to the optimal RAG paradigm (Naive, Hybrid, Graph, Corrective, or Agentic).
"""

import logging
import time
from typing import Any, Dict, Optional

from src.agentic_rag import AgenticRAG
from src.corrective_rag import CorrectiveRAG
from src.graph_rag import GraphRAG
from src.hybrid_rag import HybridRAG
from src.naive_rag import NaiveRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("RAGRouter")


class RAGRouter:
    """Intelligent Dynamic Router for Multi-Tier RAG Engines."""

    def __init__(
        self, corpus_path: Optional[str] = "data/sample_corpus.json"
    ) -> None:
        """Initialize all 5 RAG paradigm engines.

        Args:
            corpus_path: Path to sample corpus JSON file.
        """
        self.corpus_path = corpus_path
        self.naive_engine = NaiveRAG(corpus_path=corpus_path)
        self.hybrid_engine = HybridRAG(corpus_path=corpus_path)
        self.graph_engine = GraphRAG(corpus_path=corpus_path)
        self.corrective_engine = CorrectiveRAG(corpus_path=corpus_path)
        self.agentic_engine = AgenticRAG(corpus_path=corpus_path)

    def classify_query(self, query: str) -> Dict[str, Any]:
        """Classify query intent and determine optimal RAG paradigm.

        Args:
            query: User input query string.

        Returns:
            Dict containing selected paradigm name and engine instance.
        """
        q_lower = query.lower()

        agentic_triggers = [
            "decompose", "multi-step", "workflow", "agent", "reason",
            "plan", "calculate", "tool", "step by step", "complex"
        ]
        if any(trigger in q_lower for trigger in agentic_triggers):
            return {
                "paradigm": "Agentic RAG",
                "engine": self.agentic_engine,
                "reasoning": (
                    "Query requires multi-turn reasoning, decomposition, "
                    "tool invocation, or reflection."
                ),
            }

        graph_triggers = [
            "relationship", "relation", "connect", "dependency", "topology",
            "graph", "entity", "how does", "link", "hierarchy", "architecture"
        ]
        if any(trigger in q_lower for trigger in graph_triggers):
            return {
                "paradigm": "Graph RAG",
                "engine": self.graph_engine,
                "reasoning": (
                    "Query involves entity relationships, network topology, "
                    "or multi-hop knowledge graph traversal."
                ),
            }

        crag_triggers = [
            "verify", "latest", "external", "recent", "news", "check",
            "update", "fact check", "web", "current"
        ]
        if any(trigger in q_lower for trigger in crag_triggers):
            return {
                "paradigm": "Corrective RAG (CRAG)",
                "engine": self.corrective_engine,
                "reasoning": (
                    "Query requires context confidence evaluation or "
                    "dynamic web search fallback."
                ),
            }

        hybrid_triggers = [
            "bm25", "lexical", "exact", "code", "protocol", "rfc",
            "spec", "keyword", "version", "syntax"
        ]
        if (
            any(trigger in q_lower for trigger in hybrid_triggers)
            or len(q_lower.split()) > 10
        ):
            return {
                "paradigm": "Hybrid / Modular RAG",
                "engine": self.hybrid_engine,
                "reasoning": (
                    "Query contains specific technical terminology "
                    "benefiting from BM25 lexical + dense vector search."
                ),
            }

        return {
            "paradigm": "Naive RAG",
            "engine": self.naive_engine,
            "reasoning": (
                "Standard direct semantic search query routed to dense vector "
                "retrieval."
            ),
        }

    def route_and_execute(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Route query to optimal engine and return execution result.

        Args:
            query: User search query string.
            top_k: Top K results limit.

        Returns:
            Dict containing routing decision, latency, and engine response.
        """
        classification = self.classify_query(query)
        target_engine = classification["engine"]
        paradigm = classification["paradigm"]
        reasoning = classification["reasoning"]

        start_time = time.time()
        result = target_engine.generate(query)
        latency_ms = round((time.time() - start_time) * 1000, 2)

        return {
            "query": query,
            "selected_paradigm": paradigm,
            "routing_reasoning": reasoning,
            "latency_ms": latency_ms,
            "engine_output": result,
        }

    def benchmark_all_paradigms(self, query: str) -> Dict[str, Any]:
        """Execute query across all 5 RAG paradigms to benchmark latency.

        Args:
            query: Input user query.

        Returns:
            Dict containing comparative results from all 5 RAG engines.
        """
        engines = [
            ("Naive RAG", self.naive_engine),
            ("Hybrid / Modular RAG", self.hybrid_engine),
            ("Graph RAG", self.graph_engine),
            ("Corrective RAG", self.corrective_engine),
            ("Agentic RAG", self.agentic_engine),
        ]

        benchmark_results = []
        for name, engine in engines:
            start_time = time.time()
            output = engine.generate(query)
            latency = round((time.time() - start_time) * 1000, 2)
            benchmark_results.append({
                "paradigm": name,
                "latency_ms": latency,
                "response": output.get("response", ""),
            })

        return {
            "query": query,
            "benchmark_results": benchmark_results,
        }
