"""
PASHA-NEXUS-HIVE V7 - FastAPI REST Service
Exposes RESTful endpoints for autonomous agent workforce operations.
"""
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

from agents.orchestrator import SwarmOrchestrator
from core.job_scraper import JobScraper
from core.resume_tailor import ResumeTailor
from core.cover_letter_gen import CoverLetterGenerator
from core.cold_email_gen import ColdEmailGenerator
from core.interview_prep import InterviewPrepEngine
from dashboard.analytics import WorkforceAnalytics

app = FastAPI(
    title="PASHA-NEXUS-HIVE V7 API",
    description="Autonomous AI Workforce Swarm OS - 100 AI Employees REST API",
    version="7.0.0"
)

orchestrator = SwarmOrchestrator()
scraper = JobScraper()
tailorer = ResumeTailor()
cl_gen = CoverLetterGenerator()
ce_gen = ColdEmailGenerator()
ip_engine = InterviewPrepEngine()
analytics_engine = WorkforceAnalytics()

class SwarmRunRequest(BaseModel):
    jd_input: str = Field(..., description="Job Description raw text or job posting URL")
    is_url: bool = Field(False, description="Set True if jd_input is a URL")

class TailorResumeRequest(BaseModel):
    jd_title: str
    jd_company: str
    keywords: List[str]

class VoiceMockRequest(BaseModel):
    question: str
    user_transcript: str

@app.get("/")
def read_root():
    return {
        "system": "PASHA-NEXUS-HIVE V7",
        "description": "Autonomous AI Workforce Swarm OS - 100 AI Employees",
        "status": "online",
        "version": "7.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "main_api"}

@app.post("/api/v7/swarm/run")
def run_swarm_pipeline(req: SwarmRunRequest):
    try:
        result = orchestrator.run_swarm(req.jd_input, is_url=req.is_url)
        return {
            "success": True,
            "application_id": result.get("application_id"),
            "status": result.get("status"),
            "jd_info": result.get("jd_info"),
            "company_research": result.get("company_research"),
            "ats_score": result.get("tailored_resume", {}).get("ats_score"),
            "critic_eval": result.get("critic_eval"),
            "pdf_path": result.get("pdf_path")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v7/resume/tailor")
def tailor_resume(req: TailorResumeRequest):
    jd_info = {
        "title": req.jd_title,
        "company": req.jd_company,
        "keywords": req.keywords
    }
    tailored = tailorer.tailor_resume(jd_info)
    return {"success": True, "tailored_resume": tailored}

@app.post("/api/v7/generate/cover-letter")
def generate_cover_letter(req: TailorResumeRequest):
    jd_info = {
        "title": req.jd_title,
        "company": req.jd_company,
        "keywords": req.keywords
    }
    cl = cl_gen.generate_cover_letter(jd_info)
    return {"success": True, "cover_letter": cl}

@app.post("/api/v7/generate/cold-email")
def generate_cold_email(req: TailorResumeRequest):
    jd_info = {
        "title": req.jd_title,
        "company": req.jd_company,
        "keywords": req.keywords
    }
    ce = ce_gen.generate_cold_email(jd_info)
    return {"success": True, "cold_email": ce}

@app.post("/api/v7/interview/prep")
def get_interview_prep(req: TailorResumeRequest):
    jd_info = {
        "title": req.jd_title,
        "company": req.jd_company,
        "keywords": req.keywords
    }
    questions = ip_engine.generate_interview_questions(jd_info)
    return {"success": True, "questions": questions}

@app.post("/api/v7/interview/voice-mock")
def evaluate_voice_mock(req: VoiceMockRequest):
    res = ip_engine.simulate_voice_mock_response(req.question, req.user_transcript)
    return {"success": True, "evaluation": res}

@app.get("/api/v7/analytics")
def get_analytics():
    return {
        "summary": analytics_engine.get_summary_metrics()
    }
