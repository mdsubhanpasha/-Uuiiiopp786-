import os
from typing import Dict, Any, List
from loguru import logger
from app.qdrant_service import QdrantStyleService

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

class GhostwriterNode:
    """
    Node 2 - Ghostwriter
    Takes topic + angle + style vectors from Qdrant, generates 3 variants using GPT-4o:
    Variant A: Story format (personal anecdote)
    Variant B: Technical deep-dive (with metrics)
    Variant C: Contrarian hot-take
    Each 180-250 words, structure: Hook (first 2 lines must be scroll-stopper) -> Problem -> Insight with data -> CTA + Question. Include 3-5 hashtags at end.
    """
    def __init__(self):
        self.qdrant_service = QdrantStyleService()
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.client = None
        if OPENAI_AVAILABLE and self.openai_key and not self.openai_key.startswith("sk-placeholder"):
            try:
                self.client = OpenAI(api_key=self.openai_key)
            except Exception as e:
                logger.warning(f"Ghostwriter OpenAI init failed: {e}")

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Executing Node 2: Ghostwriter...")
        topic = state.get("topic", "Multi-Agent Architectures")
        angle = state.get("angle", "Contrarian")
        feedback = state.get("feedback", "")

        # Retrieve user writing style examples from Qdrant
        style_examples = self.qdrant_service.search_similar_style(query_text=topic, limit=2)
        style_context = "\n---\n".join([item["post_text"] for item in style_examples]) if style_examples else "Direct, authoritative, data-driven, concise, punchy."

        prompt = f"""You are an elite LinkedIn Ghostwriter for top AI founders and enterprise tech leaders.
Topic: {topic}
Angle: {angle}
User Past Style Examples:
{style_context}

Previous Feedback to fix (if any): {feedback}

Generate 3 DISTINCT variants for this post:
Variant A: Story format (personal anecdote or engineering journey)
Variant B: Technical deep-dive (with concrete metrics like sub-300ms, 99.4% precision, 10x throughput)
Variant C: Contrarian hot-take (challenging status quo AI architectures)

RULES FOR EACH VARIANT:
1. Word count: 180-250 words.
2. Structure:
   - Line 1-2: HOOK (must be an absolute scroll-stopper).
   - Paragraph 2: PROBLEM (the core pain point in production).
   - Paragraph 3: INSIGHT WITH DATA (the breakthrough solution with numbers/metrics).
   - Paragraph 4: CTA + QUESTION (call to action encouraging high-signal comments).
3. End with 3-5 high-performing hashtags (e.g., #VoiceAI #RAG #LangGraph #GenerativeAI).

Return your output formatted exactly as follows:

---VARIANT A---
[Full text of Variant A]

---VARIANT B---
[Full text of Variant B]

---VARIANT C---
[Full text of Variant C]
"""

        variants = {}
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are a world-class LinkedIn ghostwriter."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7
                )
                content = response.choices[0].message.content
                variants = self._parse_variants(content)
            except Exception as e:
                logger.error(f"GPT-4o ghostwriting failed: {e}. Falling back to high-quality fallback generator.")
                variants = self._generate_fallback_variants(topic, angle)
        else:
            variants = self._generate_fallback_variants(topic, angle)

        # Select variant matching current angle or default to Variant A
        selected_variant_key = "Variant A"
        if angle.lower() == "technical":
            selected_variant_key = "Variant B"
        elif angle.lower() == "contrarian":
            selected_variant_key = "Variant C"

        selected_text = variants.get(selected_variant_key, variants.get("Variant A", ""))
        parsed_parts = self._extract_structure(selected_text)

        logger.info(f"Ghostwriter generated 3 variants. Selected: {selected_variant_key}")
        return {
            "variants": variants,
            "selected_variant_type": selected_variant_key,
            "full_text": selected_text,
            "hook": parsed_parts["hook"],
            "problem": parsed_parts["problem"],
            "insight": parsed_parts["insight"],
            "cta": parsed_parts["cta"],
            "hashtags": parsed_parts["hashtags"]
        }

    def _parse_variants(self, text: str) -> Dict[str, str]:
        variants = {}
        parts = text.split("---VARIANT ")
        for part in parts:
            if not part.strip():
                continue
            lines = part.strip().split("\n")
            variant_name = f"Variant {lines[0].replace('---', '').strip()[:1]}"
            content = "\n".join(lines[1:]).strip()
            variants[variant_name] = content

        if not variants:
            variants["Variant A"] = text.strip()
        return variants

    def _generate_fallback_variants(self, topic: str, angle: str) -> Dict[str, str]:
        return {
            "Variant A": f"""Most engineering teams build AI agents wrong. They connect LLMs directly to APIs and pray it works in production.

Last month, we stress-tested a multi-agent system handling 50,000 requests/day. Without explicit state machines, agent loops degraded by 42% after 3 turns.

The solution? A deterministic LangGraph DAG architecture with stateful memory and real-time verification nodes. Latency dropped to sub-300ms while reliability hit 99.4%.

Stop shipping naive prompt wrappers. Build resilient agent loops.

How is your engineering team handling multi-agent state persistence in production?

#LangGraph #VoiceAI #RAG #MultiAgent #EnterpriseAI""",

            "Variant B": f"""Sub-300ms Voice AI is no longer a luxury—it's the baseline requirement for enterprise voice bots.

Here is the exact benchmark architecture we deployed:
1. Deepgram Nova-2 streaming STT (<120ms first byte)
2. Groq Llama-3.3-70b speculative decoding (<80ms turn)
3. ElevenLabs WebSocket streaming TTS (<100ms response)

Result: 99.4% transcription accuracy and zero perceived pause during customer interruptions.

If your voice agent latency is over 500ms, users abandon the call within 12 seconds.

What bottleneck is currently holding back your real-time voice AI stack?

#VoiceAI #Deepgram #ElevenLabs #Groq #AIInfrastructure""",

            "Variant C": f"""Unpopular opinion: 90% of enterprise RAG applications are complete overkill.

Companies spend $50k/month on vector databases and complex semantic chunking when simple structured key-value caches and hybrid BM25 search outperform them by 4x on domain data.

In our stress tests across 100,000 complex PDF contracts:
- Pure Vector Search Accuracy: 68.2%
- Hybrid Dense + BM25 + Reciprocal Rank Fusion: 94.8%

Stop relying purely on embeddings. Dense hybrid retrieval with Cross-Encoder reranking is the true gold standard.

Are you relying on pure vector embeddings or hybrid retrieval?

#RAG #Qdrant #VectorSearch #GenerativeAI #NLP"""
        }

    def _extract_structure(self, text: str) -> Dict[str, str]:
        lines = [line.strip() for line in text.strip().split("\n") if line.strip()]
        hook = lines[0] if lines else ""
        if len(lines) > 1 and not lines[1].startswith("#"):
            hook += "\n" + lines[1]

        hashtags = [line for line in lines if line.startswith("#")]
        hashtags_str = " ".join(hashtags) if hashtags else "#AI #GenerativeAI #LangGraph"

        non_hashtag_lines = [line for line in lines if not line.startswith("#")]

        problem = non_hashtag_lines[2] if len(non_hashtag_lines) > 2 else ""
        insight = non_hashtag_lines[3] if len(non_hashtag_lines) > 3 else ""
        cta = non_hashtag_lines[-1] if non_hashtag_lines else ""

        return {
            "hook": hook,
            "problem": problem,
            "insight": insight,
            "cta": cta,
            "hashtags": hashtags_str
        }
