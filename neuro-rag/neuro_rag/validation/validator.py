"""
PASHA-NEURO-RAG DeBERTa-v3 NLI Validator Agent (Hallucination Guard)
Author: Mohammad Subhan Pasha

Checks every generated answer against source context chunks using Natural Language Inference (NLI).
If answer is not grounded in source context, returns "I don't have enough info in documents".
"""

import logging
from typing import List, Dict, Any, Tuple, Optional
from pydantic import BaseModel, Field

from neuro_rag.config import settings
from neuro_rag.ingestion.schemas import Chunk

logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    is_grounded: bool
    groundedness_score: float
    entailment_details: List[Dict[str, Any]]
    final_answer: str
    rejection_reason: Optional[str] = None


class ValidatorAgent:
    """
    NLI Validator Agent acts as Hallucination Guard using DeBERTa-v3 NLI model or cross-encoder entailment scoring.
    Premise: Combined retrieved source text chunks.
    Hypothesis: Generated candidate answer statements.
    """

    FALLBACK_RESPONSE = "I don't have enough info in documents"

    def __init__(self, model_name: Optional[str] = None, threshold: Optional[float] = None):
        self.model_name = model_name or settings.NLI_MODEL_NAME
        self.threshold = threshold or settings.GROUNDEDNESS_THRESHOLD
        self._nli_pipeline = None

    def _init_pipeline(self):
        if not self._nli_pipeline:
            try:
                from transformers import pipeline
                self._nli_pipeline = pipeline(
                    "text-classification",
                    model=self.model_name,
                    top_k=None,
                    truncation=True,
                    max_length=512
                )
            except Exception as e:
                logger.warning(f"Could not load DeBERTa-v3 NLI pipeline {self.model_name}: {e}")

    def validate_answer(
        self,
        candidate_answer: str,
        source_chunks: List[Chunk]
    ) -> ValidationResult:
        if not candidate_answer or not candidate_answer.strip():
            return ValidationResult(
                is_grounded=False,
                groundedness_score=0.0,
                entailment_details=[],
                final_answer=self.FALLBACK_RESPONSE,
                rejection_reason="Empty candidate answer."
            )

        if candidate_answer.strip() == self.FALLBACK_RESPONSE:
            return ValidationResult(
                is_grounded=False,
                groundedness_score=0.0,
                entailment_details=[],
                final_answer=self.FALLBACK_RESPONSE,
                rejection_reason="Candidate answer is fallback response."
            )

        if not source_chunks:
            return ValidationResult(
                is_grounded=False,
                groundedness_score=0.0,
                entailment_details=[],
                final_answer=self.FALLBACK_RESPONSE,
                rejection_reason="No source chunks provided for grounding verification."
            )

        context_text = "\n".join([f"[{c.metadata.source_name}] {c.content}" for c in source_chunks])[:1500]

        # Split candidate answer into sentences to check statement entailment
        sentences = [s.strip() for s in candidate_answer.replace("\n", ". ").split(".") if len(s.strip()) > 5]
        if not sentences:
            sentences = [candidate_answer.strip()]

        entailment_scores = []
        details = []

        try:
            self._init_pipeline()
            if self._nli_pipeline:
                for sent in sentences:
                    inputs = f"premise: {context_text} hypothesis: {sent}"
                    res = self._nli_pipeline(inputs)
                    scores_dict = {item["label"].lower(): item["score"] for item in res[0]}
                    ent_score = scores_dict.get("entailment", scores_dict.get("label_2", 0.0))
                    entailment_scores.append(ent_score)
                    details.append({"statement": sent, "entailment_score": float(ent_score)})
        except Exception as e:
            logger.warning(f"NLI model inference error: {e}. Executing heuristic entailment validator.")

        # Fallback heuristic grounding verification if NLI model fails or is un-downloaded
        if not entailment_scores:
            for sent in sentences:
                sent_words = set(w.lower() for w in sent.split() if len(w) > 3)
                if not sent_words:
                    ent_score = 1.0
                else:
                    context_words = set(w.lower() for w in context_text.split())
                    overlap = len(sent_words.intersection(context_words)) / len(sent_words)
                    ent_score = min(1.0, overlap * 1.3)
                entailment_scores.append(ent_score)
                details.append({"statement": sent, "entailment_score": float(ent_score)})

        mean_groundedness = float(sum(entailment_scores) / max(len(entailment_scores), 1))
        is_grounded = mean_groundedness >= self.threshold

        if is_grounded:
            return ValidationResult(
                is_grounded=True,
                groundedness_score=round(mean_groundedness, 4),
                entailment_details=details,
                final_answer=candidate_answer
            )
        else:
            return ValidationResult(
                is_grounded=False,
                groundedness_score=round(mean_groundedness, 4),
                entailment_details=details,
                final_answer=self.FALLBACK_RESPONSE,
                rejection_reason=f"Groundedness score {mean_groundedness:.2f} is below threshold {self.threshold:.2f}."
            )
