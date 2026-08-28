"""
PASHA-NEXUS-HIVE V7 - LangGraph Swarm Orchestrator
6-Node StateGraph Workflow: Scrape -> Research -> Tailor -> Generate -> Critic -> Tracker.
Loops back from Critic -> Tailor if quality score < 85 (up to max 3 iterations).
"""
import os
import uuid
from typing import Dict, Any, TypedDict, List
from langgraph.graph import StateGraph, END

from core.job_scraper import JobScraper
from core.resume_tailor import ResumeTailor
from core.cover_letter_gen import CoverLetterGenerator
from core.cold_email_gen import ColdEmailGenerator
from agents.researcher_agent import CompanyResearcherAgent
from agents.critic_agent import CriticAgent

class SwarmState(TypedDict):
    application_id: str
    jd_raw_text: str
    jd_url: str
    jd_info: Dict[str, Any]
    company_research: Dict[str, Any]
    tailored_resume: Dict[str, Any]
    cover_letter: str
    cold_email: Dict[str, str]
    critic_eval: Dict[str, Any]
    iteration_count: int
    status: str
    pdf_path: str

class SwarmOrchestrator:
    def __init__(self, groq_api_key: str = None, tavily_api_key: str = None):
        self.scraper = JobScraper()
        self.researcher = CompanyResearcherAgent(tavily_api_key=tavily_api_key, groq_api_key=groq_api_key)
        self.tailorer = ResumeTailor()
        self.cl_gen = CoverLetterGenerator(groq_api_key=groq_api_key)
        self.ce_gen = ColdEmailGenerator(groq_api_key=groq_api_key)
        self.critic = CriticAgent(pass_threshold=85)
        self.graph = self._build_graph()

    def node_scrape(self, state: SwarmState) -> Dict[str, Any]:
        """Node 1: Scrape job description."""
        url = state.get("jd_url", "")
        raw = state.get("jd_raw_text", "")
        if url and not raw:
            jd_info = self.scraper.scrape_url(url)
        else:
            jd_info = self.scraper.parse_raw_text(raw or "Remote AI Engineer at Perplexity")
        return {"jd_info": jd_info, "status": "scraped"}

    def node_research(self, state: SwarmState) -> Dict[str, Any]:
        """Node 2: Company Intelligence Research."""
        jd_info = state["jd_info"]
        res = self.researcher.research_company(jd_info["company"], jd_info["title"])
        return {"company_research": res, "status": "researched"}

    def node_tailor(self, state: SwarmState) -> Dict[str, Any]:
        """Node 3: Resume Tailoring & STAR bullets rewriter."""
        jd_info = state["jd_info"]
        tailored = self.tailorer.tailor_resume(jd_info)

        # Save PDF
        app_id = state.get("application_id", str(uuid.uuid4())[:8])
        os.makedirs("outputs/tailored_resumes", exist_ok=True)
        pdf_path = f"outputs/tailored_resumes/resume_{app_id}.pdf"
        self.tailorer.generate_pdf(tailored, pdf_path)

        return {
            "tailored_resume": tailored,
            "pdf_path": pdf_path,
            "iteration_count": state.get("iteration_count", 0) + 1,
            "status": "tailored"
        }

    def node_generate(self, state: SwarmState) -> Dict[str, Any]:
        """Node 4: Generate Cover Letter and Cold Email."""
        jd_info = state["jd_info"]
        cl = self.cl_gen.generate_cover_letter(jd_info)
        ce = self.ce_gen.generate_cold_email(jd_info)

        # Save Cover Letter
        app_id = state.get("application_id", "default")
        os.makedirs("outputs/cover_letters", exist_ok=True)
        with open(f"outputs/cover_letters/cover_letter_{app_id}.txt", "w") as f:
            f.write(cl)

        return {"cover_letter": cl, "cold_email": ce, "status": "generated"}

    def node_critic(self, state: SwarmState) -> Dict[str, Any]:
        """Node 5: Quality Critic Evaluation & Scoring (0-100)."""
        resume = state["tailored_resume"]
        cl = state["cover_letter"]
        keywords = state["jd_info"].get("keywords", [])

        eval_res = self.critic.evaluate_output(resume, cl, keywords)
        return {"critic_eval": eval_res, "status": "evaluated"}

    def node_tracker(self, state: SwarmState) -> Dict[str, Any]:
        """Node 6: Pipeline Tracker & Storage."""
        return {"status": "completed"}

    def _should_loop_back(self, state: SwarmState) -> str:
        eval_res = state.get("critic_eval", {})
        count = state.get("iteration_count", 1)
        if not eval_res.get("passed", False) and count < 3:
            return "tailor"
        return "tracker"

    def _build_graph(self):
        builder = StateGraph(SwarmState)

        builder.add_node("scrape", self.node_scrape)
        builder.add_node("research", self.node_research)
        builder.add_node("tailor", self.node_tailor)
        builder.add_node("generate", self.node_generate)
        builder.add_node("critic", self.node_critic)
        builder.add_node("tracker", self.node_tracker)

        builder.set_entry_point("scrape")
        builder.add_edge("scrape", "research")
        builder.add_edge("research", "tailor")
        builder.add_edge("tailor", "generate")
        builder.add_edge("generate", "critic")

        builder.add_conditional_edges(
            "critic",
            self._should_loop_back,
            {
                "tailor": "tailor",
                "tracker": "tracker"
            }
        )
        builder.add_edge("tracker", END)
        return builder.compile()

    def run_swarm(self, jd_input: str, is_url: bool = False) -> Dict[str, Any]:
        app_id = str(uuid.uuid4())[:8]
        initial_state: SwarmState = {
            "application_id": app_id,
            "jd_raw_text": jd_input if not is_url else "",
            "jd_url": jd_input if is_url else "",
            "jd_info": {},
            "company_research": {},
            "tailored_resume": {},
            "cover_letter": "",
            "cold_email": {},
            "critic_eval": {},
            "iteration_count": 0,
            "status": "started",
            "pdf_path": ""
        }

        final_state = self.graph.invoke(initial_state)
        return final_state
