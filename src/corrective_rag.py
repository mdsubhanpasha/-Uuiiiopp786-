"""Corrective RAG (CRAG) Engine implementation.

Evaluates document retrieval relevance confidence scores and dynamically
triggers fallback web search when context confidence drops below 0.65.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from src.naive_rag import NaiveRAG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CorrectiveRAG")


class CorrectiveRAG:
    """Evaluator-guided Corrective RAG engine with web search fallback."""

    def __init__(
        self,
        corpus_path: Optional[str] = None,
        confidence_threshold: float = 0.65,
    ) -> None:
        """Initialize CorrectiveRAG instance.

        Args:
            corpus_path: Path to sample corpus JSON file.
            confidence_threshold: Evaluator threshold score (default 0.65).
        """
        self.confidence_threshold = confidence_threshold
        self.vector_engine = NaiveRAG(corpus_path=corpus_path)

    def evaluate_retrieval_confidence(
        self, query: str, retrieved_docs: List[Tuple[Dict[str, Any], float]]
    ) -> Tuple[float, str]:
        """Assess overall confidence score of retrieved documents for query.

        Args:
            query: User search query.
            retrieved_docs: List of (doc_dict, vector_score) retrieved.

        Returns:
            Tuple of (confidence_score, action).
        """
        if not retrieved_docs:
            return 0.0, "INCORRECT"

        query_tokens = set(query.lower().split())
        top_doc, top_score = retrieved_docs[0]

        content_tokens = set(top_doc.get("content", "").lower().split())
        title_tokens = set(top_doc.get("title", "").lower().split())

        doc_tokens = content_tokens.union(title_tokens)
        overlap = len(query_tokens.intersection(doc_tokens))
        token_ratio = overlap / max(1, len(query_tokens))

        confidence = (top_score * 0.6) + (token_ratio * 0.4)
        confidence = min(1.0, max(0.0, confidence))

        if confidence >= self.confidence_threshold:
            action = "CORRECT"
        elif confidence >= 0.40:
            action = "AMBIGUOUS"
        else:
            action = "INCORRECT"

        logger.info(
            "CRAG Evaluator confidence: %.4f | Assessment: %s",
            confidence,
            action,
        )
        return float(confidence), action

    def fallback_web_search(self, query: str) -> List[Dict[str, Any]]:
        """Execute dynamic fallback web search simulation / Tavily API call.

        Args:
            query: Query string or re-written query.

        Returns:
            List of web search result document dicts.
        """
        logger.info("Executing Fallback Web Search for query: '%s'", query)

        web_results = [
            {
                "id": "web-001",
                "title": f"Live Web Intelligence: {query.capitalize()}",
                "content": (
                    f"External Web Search Insights on '{query}': Updated "
                    f"enterprise documentation indicates recent patches "
                    f"and deployment specifications."
                ),
                "source": "Tavily Web Crawler",
            },
            {
                "id": "web-002",
                "title": "Global Cloud & Security Bulletin",
                "content": (
                    f"Current global standards regarding '{query}' recommend "
                    f"zero-trust authentication and automated failover."
                ),
                "source": "Serper Global Index",
            },
        ]
        return web_results

    def rewrite_query(self, query: str) -> str:
        """Transform user query to optimize for web search retrieval.

        Args:
            query: Original user query.

        Returns:
            Re-written query string.
        """
        cleaned = query.replace("?", "").replace("!", "").strip()
        rewritten = f"enterprise infrastructure best practices for {cleaned}"
        logger.info("Query rewritten: '%s' -> '%s'", query, rewritten)
        return rewritten

    def generate(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Execute Corrective RAG evaluation and dynamic context generation.

        Args:
            query: User query string.
            top_k: Top K document limit.

        Returns:
            Dictionary containing evaluation score, action, and response.
        """
        retrieved_docs = self.vector_engine.retrieve(query, top_k=top_k)
        confidence, action = self.evaluate_retrieval_confidence(
            query, retrieved_docs
        )

        web_docs: List[Dict[str, Any]] = []
        final_contexts: List[str] = []

        if action == "CORRECT":
            final_contexts = [
                f"[Vector Doc] {doc['title']}: {doc['content']}"
                for doc, _ in retrieved_docs
            ]
            eval_summary = (
                f"Retrieved docs matched high confidence threshold "
                f"({confidence:.2f} >= {self.confidence_threshold})."
            )

        elif action == "AMBIGUOUS":
            rewritten_q = self.rewrite_query(query)
            web_docs = self.fallback_web_search(rewritten_q)
            vector_ctx = [
                f"[Internal Doc] {doc['title']}: {doc['content']}"
                for doc, _ in retrieved_docs[:1]
            ]
            web_ctx = [
                f"[Web Doc] {doc['title']}: {doc['content']}"
                for doc in web_docs[:1]
            ]
            final_contexts = vector_ctx + web_ctx
            eval_summary = (
                f"Internal retrieval confidence was moderate "
                f"({confidence:.2f}). Triggered web search fallback."
            )

        else:  # INCORRECT
            rewritten_q = self.rewrite_query(query)
            web_docs = self.fallback_web_search(rewritten_q)
            final_contexts = [
                f"[Web Doc] {doc['title']}: {doc['content']}"
                for doc in web_docs
            ]
            eval_summary = (
                f"Internal retrieval confidence was below threshold "
                f"({confidence:.2f} < 0.40). Executed web search fallback."
            )

        response_text = (
            f"[Corrective RAG (CRAG) Response]\n"
            f"Evaluator Score: {confidence:.4f} | Action: {action}\n"
            f"Assessment: {eval_summary}\n\n"
            "Context Payload:\n" + "\n".join(final_contexts) + "\n\n"
            "Final Synthesized Answer: Enterprise answer generated safely."
        )

        return {
            "paradigm": "Corrective RAG (CRAG)",
            "query": query,
            "confidence_score": round(confidence, 4),
            "corrective_action": action,
            "fallback_triggered": action in ("AMBIGUOUS", "INCORRECT"),
            "used_web_search": len(web_docs) > 0,
            "response": response_text,
        }
