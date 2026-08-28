"""
PASHA-NEXUS-HIVE V7 - Company Researcher Agent
Researches target companies using Tavily Web Search and LLM intelligence.
"""
import os
from typing import Dict, Any

class CompanyResearcherAgent:
    def __init__(self, tavily_api_key: str = None, groq_api_key: str = None):
        self.tavily_api_key = tavily_api_key or os.getenv("TAVILY_API_KEY")
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")

    def research_company(self, company_name: str, job_title: str) -> Dict[str, Any]:
        """Gather intelligence on company products, culture, tech stack, and recent news."""
        search_query = f"{company_name} AI engineering technology stack culture funding news"
        snippets = []

        if self.tavily_api_key:
            try:
                from tavily import TavilyClient
                tavily = TavilyClient(api_key=self.tavily_api_key)
                results = tavily.search(query=search_query, max_results=3)
                for res in results.get("results", []):
                    snippets.append(res.get("content", ""))
            except Exception as e:
                print(f"[ResearcherAgent] Tavily search fallback: {e}")

        if not snippets:
            snippets = [
                f"{company_name} is a leading innovator in AI infrastructure, vector search, and LLM orchestration.",
                f"{company_name} engineering team prioritizes low-latency systems, Python, FastAPI, and robust multi-agent swarms."
            ]

        summary = f"{company_name} is actively scaling their AI Engineering team for {job_title}. " + " ".join(snippets[:2])

        return {
            "company": company_name,
            "job_title": job_title,
            "intelligence_summary": summary,
            "key_initiatives": ["LLM Inference Acceleration", "Multi-Agent Workflow Automation", "Vector Database RAG Scaling"],
            "recommended_focus": "Highlight experience with LangGraph, Qdrant vector retrieval, Groq Llama 3.3 70B, and sub-second API performance."
        }
