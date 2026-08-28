"""
PASHA-NEXUS-HIVE V7 Unit Tests
"""
import pytest
import os
import sys

# Add path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.job_scraper import JobScraper
from core.resume_tailor import ResumeTailor, DEFAULT_BASE_RESUME
from core.cover_letter_gen import CoverLetterGenerator
from core.cold_email_gen import ColdEmailGenerator
from core.interview_prep import InterviewPrepEngine
from agents.researcher_agent import CompanyResearcherAgent
from agents.critic_agent import CriticAgent
from agents.orchestrator import SwarmOrchestrator
from dashboard.analytics import WorkforceAnalytics

def test_job_scraper():
    scraper = JobScraper()
    raw = "Title: AI Engineer\nCompany: Perplexity\nSalary: $120,000\nRequirements:\n- LangGraph\n- Qdrant"
    res = scraper.parse_raw_text(raw)
    assert res["title"] == "AI Engineer"
    assert res["company"] == "Perplexity"
    assert "LangGraph" in res["keywords"]

def test_resume_tailor():
    tailor = ResumeTailor()
    jd_info = {"title": "AI Engineer", "company": "Vercel", "keywords": ["LangGraph", "FastAPI"]}
    tailored = tailor.tailor_resume(jd_info)
    assert "Vercel" in tailored["summary"]
    assert tailored["ats_score"] >= 85

    output_pdf = "outputs/tailored_resumes/test_resume.pdf"
    path = tailor.generate_pdf(tailored, output_pdf)
    assert os.path.exists(path)

def test_cover_letter_gen():
    gen = CoverLetterGenerator()
    jd_info = {"title": "Staff AI Engineer", "company": "Anthropic", "keywords": ["RAG", "Qdrant"]}
    cl = gen.generate_cover_letter(jd_info)
    assert "Anthropic" in cl
    assert "PASHA-OS" in cl

def test_cold_email_gen():
    gen = ColdEmailGenerator()
    jd_info = {"title": "AI Architect", "company": "OpenAI", "keywords": ["LangGraph"]}
    ce = gen.generate_cold_email(jd_info)
    assert "subject" in ce
    assert "OpenAI" in ce["subject"]

def test_interview_prep():
    engine = InterviewPrepEngine()
    jd_info = {"title": "AI Engineer", "company": "Scale AI"}
    q = engine.generate_interview_questions(jd_info)
    assert len(q) >= 3

    mock_eval = engine.simulate_voice_mock_response(q[0]["question"], "In my situation at PASHA-OS I engineered a 25 agent swarm.")
    assert mock_eval["score"] >= 60

def test_researcher_agent():
    agent = CompanyResearcherAgent()
    res = agent.research_company("Perplexity", "AI Engineer")
    assert res["company"] == "Perplexity"

def test_critic_agent():
    agent = CriticAgent(pass_threshold=85)
    resume = {"ats_score": 95}
    cl = "PASHA-OS NEURO-RAG VOX-AI PASHA-UNIFIED-OS AUTO-GROWTH PASHA-GLASS [STAR] [STAR] [STAR]"
    res = agent.evaluate_output(resume, cl, ["LangGraph"])
    assert res["score"] >= 85
    assert res["passed"] is True

def test_orchestrator():
    orchestrator = SwarmOrchestrator()
    res = orchestrator.run_swarm("Company: Vercel\nTitle: Remote AI Systems Engineer\nRequirements:\n- LangGraph\n- Qdrant")
    assert res["status"] == "completed"
    assert res["tailored_resume"]["ats_score"] >= 85
    assert os.path.exists(res["pdf_path"])

def test_analytics():
    analytics = WorkforceAnalytics()
    summary = analytics.get_summary_metrics()
    assert summary["total_applications"] == 128
    assert analytics.generate_pipeline_funnel() is not None
