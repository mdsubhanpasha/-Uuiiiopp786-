"""
PASHA-NEURO-RAG Self-Correcting LangGraph State & Orchestration
Author: Mohammad Subhan Pasha

Self-RAG Loop: Generate -> Critique -> Retrieve again if confidence < 0.85 -> Regenerate -> Validate -> Output.
"""

import json
import logging
from typing import List, Dict, Any, Optional, TypedDict
from pydantic import BaseModel, Field

from langgraph.graph import StateGraph, END
from neuro_rag.config import settings
from neuro_rag.ingestion.schemas import Chunk
from neuro_rag.retrieval.hybrid_search import HybridSearchEngine
from neuro_rag.validation.validator import ValidatorAgent, ValidationResult

logger = logging.getLogger(__name__)


class RAGState(TypedDict):
    original_query: str
    current_query: str
    retrieved_chunks: List[Chunk]
    candidate_answer: str
    critique_score: float
    critique_feedback: str
    iteration: int
    is_grounded: bool
    groundedness_score: float
    final_answer: str
    citations: List[Dict[str, Any]]


class SelfCorrectingRAGGraph:
    """
    LangGraph self-correcting RAG workflow orchestrator.
    """

    def __init__(self, search_engine: HybridSearchEngine, validator_agent: Optional[ValidatorAgent] = None):
        self.search_engine = search_engine
        self.validator_agent = validator_agent or ValidatorAgent()
        self.workflow = self._build_graph()

    def _retrieve_node(self, state: RAGState) -> RAGState:
        query = state["current_query"]
        logger.info(f"RetrieveNode executing query: '{query}' (iteration {state['iteration']})")
        chunks = self.search_engine.hybrid_search(query, top_k_retrieval=settings.TOP_K_RETRIEVAL, top_k_rerank=settings.TOP_K_RERANK)
        state["retrieved_chunks"] = chunks
        return state

    def _generate_node(self, state: RAGState) -> RAGState:
        query = state["current_query"]
        chunks = state["retrieved_chunks"]
        logger.info(f"GenerateNode generating answer for query: '{query}' with {len(chunks)} chunks")

        context_str = "\n\n".join([f"Source [{c.metadata.source_name} - Chunk {c.metadata.chunk_index}]:\n{c.content}" for c in chunks])

        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-placeholder"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                prompt = (
                    f"System: You are PASHA-NEURO-RAG, an enterprise AI assistant by Mohammad Subhan Pasha.\n"
                    f"Answer the user query concisely using ONLY the provided context documents.\n"
                    f"Include explicit inline source citations like [Source: source_name].\n\n"
                    f"Context:\n{context_str}\n\n"
                    f"User Query: {query}"
                )
                resp = client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.2
                )
                answer = resp.choices[0].message.content
            except Exception as e:
                logger.warning(f"OpenAI GPT-4o call failed: {e}. Utilizing synthesized response.")
                answer = self._synthesize_fallback_answer(query, chunks)
        else:
            answer = self._synthesize_fallback_answer(query, chunks)

        state["candidate_answer"] = answer
        return state

    def _synthesize_fallback_answer(self, query: str, chunks: List[Chunk]) -> str:
        if not chunks:
            return "I don't have enough info in documents"
        lines = [f"Based on the enterprise documents: {chunks[0].content} [Source: {chunks[0].metadata.source_name}]"]
        if len(chunks) > 1:
            lines.append(f"Additional detail: {chunks[1].content} [Source: {chunks[1].metadata.source_name}]")
        return " ".join(lines)

    def _critique_node(self, state: RAGState) -> RAGState:
        query = state["original_query"]
        answer = state["candidate_answer"]
        chunks = state["retrieved_chunks"]
        logger.info(f"CritiqueNode evaluating answer quality (iteration {state['iteration']})")

        if not chunks:
            state["critique_score"] = 0.0
            state["critique_feedback"] = "No context chunks retrieved."
            return state

        # Evaluate relevance & completeness of answer against query
        query_words = set(w.lower() for w in query.split() if len(w) > 3)
        answer_words = set(w.lower() for w in answer.split())

        if not query_words:
            overlap = 1.0
        else:
            overlap = len(query_words.intersection(answer_words)) / len(query_words)

        length_bonus = 0.2 if len(answer.split()) > 15 else 0.05
        citation_bonus = 0.2 if "[Source:" in answer or "Source" in answer else 0.0

        confidence_score = min(1.0, overlap * 0.6 + length_bonus + citation_bonus)

        # Allow LLM self-critique if API key available
        if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("sk-placeholder"):
            try:
                from openai import OpenAI
                client = OpenAI(api_key=settings.OPENAI_API_KEY)
                critique_prompt = (
                    f"Rate the confidence and accuracy of the following answer to the query on a scale of 0.0 to 1.0.\n"
                    f"Query: {query}\nAnswer: {answer}\n"
                    f"Return JSON format: {{\"confidence\": 0.9, \"feedback\": \"Explanations...\"}}"
                )
                res = client.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[{"role": "user", "content": critique_prompt}],
                    response_format={"type": "json_object"}
                )
                data = json.loads(res.choices[0].message.content)
                confidence_score = float(data.get("confidence", confidence_score))
                state["critique_feedback"] = data.get("feedback", "Self-RAG evaluation complete.")
            except Exception:
                state["critique_feedback"] = f"Heuristic self-critique score: {confidence_score:.2f}"
        else:
            state["critique_feedback"] = f"Heuristic self-critique score: {confidence_score:.2f}"

        state["critique_score"] = round(confidence_score, 4)
        return state

    def _refine_query_node(self, state: RAGState) -> RAGState:
        orig = state["original_query"]
        iter_cnt = state["iteration"] + 1
        logger.info(f"RefineQueryNode refining query from '{orig}' (iteration {iter_cnt})")

        refined = f"{orig} technical architecture overview details key components"
        if iter_cnt == 2:
            refined = f"{orig} specific implementation specifications Mohammad Subhan Pasha"

        state["current_query"] = refined
        state["iteration"] = iter_cnt
        return state

    def _validate_node(self, state: RAGState) -> RAGState:
        answer = state["candidate_answer"]
        chunks = state["retrieved_chunks"]
        logger.info("ValidateNode verifying NLI groundedness against source chunks")

        val_result: ValidationResult = self.validator_agent.validate_answer(answer, chunks)
        state["is_grounded"] = val_result.is_grounded
        state["groundedness_score"] = val_result.groundedness_score
        state["final_answer"] = val_result.final_answer

        # Build citations list
        citations = []
        for c in chunks:
            citations.append({
                "chunk_id": c.chunk_id,
                "source_name": c.metadata.source_name,
                "source_type": c.metadata.source_type,
                "uri": c.metadata.uri,
                "token_count": c.metadata.token_count,
                "relevance_score": c.metadata.semantic_score,
                "snippet": c.content[:200] + "..." if len(c.content) > 200 else c.content
            })
        state["citations"] = citations
        return state

    def _should_regenerate(self, state: RAGState) -> str:
        score = state["critique_score"]
        iter_cnt = state["iteration"]
        thresh = settings.CONFIDENCE_THRESHOLD
        max_iter = settings.MAX_SELF_CORRECTION_ITERATIONS

        if score < thresh and iter_cnt < max_iter:
            logger.info(f"Self-RAG Loop Decision: Confidence {score:.2f} < Threshold {thresh:.2f}. Triggering query refinement & re-retrieval.")
            return "refine_query"
        else:
            logger.info(f"Self-RAG Loop Decision: Confidence {score:.2f} >= Threshold {thresh:.2f} (or max iterations reached). Proceeding to validation.")
            return "validate"

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(RAGState)

        builder.add_node("retrieve", self._retrieve_node)
        builder.add_node("generate", self._generate_node)
        builder.add_node("critique", self._critique_node)
        builder.add_node("refine_query", self._refine_query_node)
        builder.add_node("validate", self._validate_node)

        builder.set_entry_point("retrieve")
        builder.add_edge("retrieve", "generate")
        builder.add_edge("generate", "critique")

        builder.add_conditional_edges(
            "critique",
            self._should_regenerate,
            {
                "refine_query": "refine_query",
                "validate": "validate"
            }
        )

        builder.add_edge("refine_query", "retrieve")
        builder.add_edge("validate", END)

        return builder.compile()

    def run(self, query: str) -> RAGState:
        initial_state: RAGState = {
            "original_query": query,
            "current_query": query,
            "retrieved_chunks": [],
            "candidate_answer": "",
            "critique_score": 0.0,
            "critique_feedback": "",
            "iteration": 1,
            "is_grounded": False,
            "groundedness_score": 0.0,
            "final_answer": "",
            "citations": []
        }
        final_state = self.workflow.invoke(initial_state)
        return final_state
