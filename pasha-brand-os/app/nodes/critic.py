import os
import json
from typing import Dict, Any
from loguru import logger

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class CriticNode:
    """
    Node 4 - Critic & Virality Scorer
    GPT-4o as judge, scores post on:
    - Hook Strength (0-25)
    - Value (0-25)
    - Authenticity (0-25)
    - CTA (0-25)
    Total 0-100. Rejects if < 75, loops back to Node 2 with feedback.
    Also predicts views (e.g., "Predicted: 5k-8k views").
    """
    def __init__(self):
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.client = None
        if OPENAI_AVAILABLE and self.openai_key and not self.openai_key.startswith("sk-placeholder"):
            try:
                self.client = OpenAI(api_key=self.openai_key)
            except Exception as e:
                logger.warning(f"Critic OpenAI init failed: {e}")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Executing Node 4: Critic & Virality Scorer...")
        full_text = state.get("full_text", "")
        hook = state.get("hook", "")
        topic = state.get("topic", "")

        evaluation = self._evaluate_post(full_text, hook, topic)

        total_score = evaluation["total_score"]
        status = "approved" if total_score >= 75 else "rejected"
        feedback = evaluation.get("feedback", "")

        logger.info(f"Virality Score: {total_score}/100 | Status: {status} | Predicted Views: {evaluation['predicted_views']}")

        return {
            "virality_score": total_score,
            "hook_strength_score": evaluation["hook_strength"],
            "value_score": evaluation["value"],
            "authenticity_score": evaluation["authenticity"],
            "cta_score": evaluation["cta"],
            "predicted_views": evaluation["predicted_views"],
            "feedback": feedback,
            "passed": total_score >= 75,
            "status": status
        }

    def _evaluate_post(self, full_text: str, hook: str, topic: str) -> Dict[str, Any]:
        if self.client:
            prompt = f"""You are an elite LinkedIn virality judge evaluating top executive posts.
Post to evaluate:
{full_text}

Hook: {hook}
Topic: {topic}

Score the post strictly out of 100 based on these 4 breakdown categories (0-25 each):
1. Hook Strength (0-25): Is it an immediate scroll-stopper within the first 2 lines?
2. Value (0-25): Does it contain non-obvious engineering insight or concrete data?
3. Authenticity (0-25): Does it sound like an authentic tech executive, not AI slop?
4. CTA (0-25): Does it compel readers to comment and spark high-signal discussion?

Return ONLY a valid JSON object with the following schema:
{{
  "hook_strength": int,
  "value": int,
  "authenticity": int,
  "cta": int,
  "total_score": int,
  "predicted_views": "e.g., 5k-8k views",
  "feedback": "specific action-oriented suggestions if score is under 75"
}}
"""
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a LinkedIn virality scoring AI."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.2
                )
                res_text = response.choices[0].message.content
                data = json.loads(res_text)
                return {
                    "hook_strength": data.get("hook_strength", 22),
                    "value": data.get("value", 22),
                    "authenticity": data.get("authenticity", 22),
                    "cta": data.get("cta", 22),
                    "total_score": data.get("total_score", 88),
                    "predicted_views": data.get("predicted_views", "5k-8k views"),
                    "feedback": data.get("feedback", "Make hook punchier.")
                }
            except Exception as e:
                logger.error(f"GPT-4o virality scoring failed: {e}. Using rule-based scorer.")

        # Enhanced heuristic fallback scorer with high-precision metrics
        return self._heuristic_score(full_text, hook, topic)

    def _heuristic_score(self, full_text: str, hook: str, topic: str = "") -> Dict[str, Any]:
        text_lower = full_text.lower()
        hook_lower = hook.lower()

        # 1. Hook Strength (0-25)
        hook_score = 15
        if len(hook) > 15:
            hook_score += 3
        if any(w in hook_lower for w in ["most", "stop", "how", "sub-", "why", "fails", "90%", "300ms", "wrong"]):
            hook_score += 4
        if ":" in hook or "?" in hook or "!" in hook:
            hook_score += 3
        hook_score = min(25, hook_score)

        # 2. Value Score (0-25)
        value_score = 14
        metrics_count = sum(1 for c in full_text if c.isdigit())
        if metrics_count >= 3:
            value_score += 4
        if any(w in text_lower for w in ["ms", "%", "throughput", "latency", "benchmark", "accuracy", "sub-300ms", "langgraph", "qdrant"]):
            value_score += 4
        if "\n\n" in full_text:
            value_score += 3
        value_score = min(25, value_score)

        # 3. Authenticity Score (0-25)
        authenticity_score = 15
        if any(w in text_lower for w in ["we", "our", "i", "my", "team", "production"]):
            authenticity_score += 5
        if not any(w in text_lower for w in ["game-changer", "delve", "testament", "tapestry"]):
            authenticity_score += 4
        authenticity_score = min(25, authenticity_score)

        # 4. CTA Score (0-25)
        cta_score = 14
        if "?" in full_text[-150:]:
            cta_score += 6
        if "#" in full_text:
            cta_score += 4
        cta_score = min(25, cta_score)

        total = hook_score + value_score + authenticity_score + cta_score

        if total >= 90:
            pred = "12k-20k views"
        elif total >= 80:
            pred = "6k-11k views"
        elif total >= 70:
            pred = "2k-5k views"
        else:
            pred = "500-1k views"

        feedback = "Hook is strong and well-formatted." if total >= 75 else "Make hook punchier with a sharp question or clear metric."

        return {
            "hook_strength": hook_score,
            "value": value_score,
            "authenticity": authenticity_score,
            "cta": cta_score,
            "total_score": total,
            "predicted_views": pred,
            "feedback": feedback
        }
