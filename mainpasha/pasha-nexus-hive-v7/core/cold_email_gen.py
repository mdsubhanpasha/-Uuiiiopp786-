"""
PASHA-NEXUS-HIVE V7 - Cold Email Generator Module
Generates high-converting, concise cold emails for CTOs/Recruiters targeting remote AI roles.
"""
import os
import json
from typing import Dict, Any

class ColdEmailGenerator:
    def __init__(self, groq_api_key: str = None):
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

    def generate_cold_email(self, jd_info: Dict[str, Any], recipient_role: str = "CTO") -> Dict[str, str]:
        company = jd_info.get("company", "Target Company")
        title = jd_info.get("title", "AI Engineer")
        keywords = ", ".join(jd_info.get("keywords", ["LangGraph", "FastAPI", "Qdrant"])[:3])

        if self.groq_api_key:
            try:
                from groq import Groq
                client = Groq(api_key=self.groq_api_key)
                prompt = f"""Write a high-converting, punchy cold email to the {recipient_role} at {company} regarding the {title} position.
Key tech focus: {keywords}.
Highlight top engineering achievements:
- 25-Agent LangGraph Swarm OS
- 0.96 RAGAS Qdrant Hybrid RAG
- <300ms real-time VOX-AI voice engine

Output JSON format with keys "subject" and "body". Body must be under 150 words."""

                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=350,
                    response_format={"type": "json_object"}
                )
                data = json.loads(response.choices[0].message.content)
                return {
                    "subject": data.get("subject", f"Building Autonomous Agent Swarms for {company}?"),
                    "body": data.get("body", "")
                }
            except Exception as e:
                print(f"[ColdEmailGenerator] Fallback triggered: {e}")

        # Fallback concise template
        subject = f"Building Autonomous Agent Swarms for {company}'s {title} role?"
        body = f"""Hi {recipient_role} at {company},

I saw {company} is scaling for the {title} role requiring expertise in {keywords}.

I recently architected 6 Autonomous AI Operating Systems, including:
1. PASHA-OS: 25-Agent MNC Swarm using LangGraph & FastAPI (<800ms latency).
2. NEURO-RAG: Self-correcting RAG engine with Qdrant vector DB hitting 0.96 RAGAS score.
3. VOX-AI: Streaming voice assistant with Deepgram & ElevenLabs (<300ms latency).

I'd love to share how I can bring this immediate multi-agent pipeline velocity to {company}. Are you open to a brief 10-minute chat this week?

Best regards,

Mohammad Subhan Pasha
Principal AI Engineer | subhanpasha@nexus-hive.ai
GitHub: github.com/mdsubhanpasha
"""
        return {"subject": subject, "body": body}
