"""LangGraph Meeting Orchestrator for Daily Standups, Weekly Department Meetings, and Monthly Board Meetings.

Saves transcripts and executive artifacts to `/artifacts/meetings/`.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Any, TypedDict

# Import all 20 agents + Validator & Critic
from agents.strategy_agent import CEOAgent, ceo_app, CEOState
from agents.cfo_agent import CFOAgent
from agents.cto_agent import CTOAgent
from agents.cmo_agent import CMOAgent
from agents.coo_agent import COOAgent
from agents.chro_agent import CHROAgent
from agents.legal_agent import LegalAgent
from agents.staff_engineer_agent import StaffEngineerAgent
from agents.qa_agent import QAAgent
from agents.devops_agent import DevOpsAgent
from agents.security_agent import SecurityAgent
from agents.data_scientist_agent import DataScientistAgent
from agents.ml_engineer_agent import MLEngineerAgent
from agents.analytics_agent import AnalyticsAgent
from agents.research_agent import ResearchAgent
from agents.product_manager_agent import ProductManagerAgent
from agents.ux_research_agent import UXResearchAgent
from agents.growth_hacker_agent import GrowthHackerAgent
from agents.sales_agent import SalesAgent
from agents.customer_success_agent import CustomerSuccessAgent
from agents.validator_agent import ValidatorAgent
from agents.critic_agent import CriticAgent


class MeetingState(TypedDict):
    """LangGraph Meeting State definition."""

    meeting_type: str
    department: str
    transcripts: List[Dict[str, Any]]
    aggregated_kpis: Dict[str, Any]
    board_decision: str
    overall_risk_score: float


class MeetingOrchestrator:
    """Orchestrates multi-agent meetings using LangGraph workflows and persists transcripts."""

    def __init__(self, artifacts_dir: str = "artifacts/meetings") -> None:
        """Initialize Meeting Orchestrator and instantiate all 20 agents.

        Args:
            artifacts_dir (str): Directory path for meeting transcript logs.
        """
        self.artifacts_dir = artifacts_dir
        os.makedirs(self.artifacts_dir, exist_ok=True)

        # Initialize all 20 Autonomous Agents
        self.ceo = CEOAgent()
        self.cfo = CFOAgent()
        self.cto = CTOAgent()
        self.cmo = CMOAgent()
        self.coo = COOAgent()
        self.chro = CHROAgent()
        self.legal = LegalAgent()

        self.staff_engineer = StaffEngineerAgent()
        self.qa = QAAgent()
        self.devops = DevOpsAgent()
        self.security = SecurityAgent()

        self.data_scientist = DataScientistAgent()
        self.ml_engineer = MLEngineerAgent()
        self.analytics = AnalyticsAgent()
        self.research = ResearchAgent()

        self.product_manager = ProductManagerAgent()
        self.ux_research = UXResearchAgent()
        self.growth_hacker = GrowthHackerAgent()

        self.sales = SalesAgent()
        self.customer_success = CustomerSuccessAgent()

        self.validator = ValidatorAgent()
        self.critic = CriticAgent()

    def _save_transcript(self, meeting_name: str, transcript_data: Dict[str, Any]) -> str:
        """Save transcript dictionary to JSON and Markdown in artifacts directory.

        Args:
            meeting_name (str): Meeting identifier prefix.
            transcript_data (Dict[str, Any]): Full meeting payload.

        Returns:
            str: Path of saved JSON transcript.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_base = f"{meeting_name}_{timestamp}"
        json_path = os.path.join(self.artifacts_dir, f"{file_base}.json")
        md_path = os.path.join(self.artifacts_dir, f"{file_base}.md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(transcript_data, f, indent=2, default=str)

        dept_str = transcript_data.get('department', 'ALL')
        md_lines = [
            f"# PASHA-OS Meeting Transcript: {meeting_name.upper().replace('_', ' ')}",
            f"**Timestamp:** {transcript_data.get('timestamp')}",
            f"**Type:** {transcript_data.get('meeting_type')} | **Department:** {dept_str}",
            "\n---",
            "## Executive Summary & Decisions",
            f"```json\n{json.dumps(transcript_data.get('summary', {}), indent=2)}\n```",
            "\n---",
            "## Agent Statements & ReAct Decisions",
        ]

        for entry in transcript_data.get("agent_statements", []):
            md_lines.append(f"### 🤖 {entry.get('agent_name')} ({entry.get('division')})")
            md_lines.append(f"**Reasoning:** {entry.get('reasoning')}")
            md_lines.append(f"**Final Decision:** `{entry.get('final_decision')}`")
            md_lines.append(f"**Confidence Score:** {entry.get('confidence_score')}")
            md_lines.append("")

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(md_lines))

        return json_path

    def run_daily_standup(self) -> Dict[str, Any]:
        """Execute Daily Standup meeting with all 20 autonomous agents.

        Returns:
            Dict[str, Any]: Standup meeting transcript report.
        """
        all_agents = [
            self.ceo, self.cfo, self.cto, self.cmo, self.coo, self.chro, self.legal,
            self.staff_engineer, self.qa, self.devops, self.security,
            self.data_scientist, self.ml_engineer, self.analytics, self.research,
            self.product_manager, self.ux_research, self.growth_hacker,
            self.sales, self.customer_success,
        ]

        agent_statements = []
        for agent in all_agents:
            res = agent.format_decision(
                reasoning=f"{agent.agent_name} operational status nominal. Daily KPIs on track.",
                data_sources=["Daily Agent Telemetry"],
                alternatives_considered=["Maintain focus on key sprint milestone"],
                final_decision=f"{agent.role} - Sprint Goal Active",
                confidence_score=0.98,
            )
            agent_statements.append(res)

        transcript = {
            "timestamp": datetime.now().isoformat(),
            "meeting_type": "DAILY_STANDUP",
            "department": "ALL_20_AGENTS",
            "summary": {"total_participants": len(all_agents), "status": "NOMINAL_ALL_SYSTEMS_GO"},
            "agent_statements": agent_statements,
        }

        json_path = self._save_transcript("daily_standup", transcript)
        transcript["transcript_file"] = json_path
        return transcript

    def run_weekly_department_meeting(self, department: str = "ENGINEERING DIVISION") -> Dict[str, Any]:
        """Execute Weekly Department Meeting for specific division.

        Args:
            department (str): Target division name.

        Returns:
            Dict[str, Any]: Department meeting transcript report.
        """
        dept_agents_map = {
            "ENGINEERING DIVISION": [self.cto, self.staff_engineer, self.qa, self.devops, self.security],
            "DATA & AI DIVISION": [self.data_scientist, self.ml_engineer, self.analytics, self.research],
            "PRODUCT & GROWTH DIVISION": [self.product_manager, self.ux_research, self.growth_hacker],
            "CUSTOMER & SALES DIVISION": [self.sales, self.customer_success],
        }

        agents = dept_agents_map.get(department, [self.cto, self.staff_engineer])
        agent_statements = []

        for agent in agents:
            if isinstance(agent, CTOAgent):
                statement = agent.evaluate_tech_stack()
            elif isinstance(agent, StaffEngineerAgent):
                statement = agent.design_architecture_and_code()
            elif isinstance(agent, QAAgent):
                statement = agent.generate_and_audit_tests()
            elif isinstance(agent, DevOpsAgent):
                statement = agent.audit_infrastructure_and_healing()
            elif isinstance(agent, SecurityAgent):
                statement = agent.scan_vulnerabilities()
            elif isinstance(agent, DataScientistAgent):
                statement = agent.train_and_track_model()
            elif isinstance(agent, MLEngineerAgent):
                statement = agent.deploy_and_monitor_model()
            elif isinstance(agent, AnalyticsAgent):
                statement = agent.track_kpis_and_bi()
            elif isinstance(agent, ResearchAgent):
                statement = agent.execute_deep_research("Enterprise MNC Department Trends")
            elif isinstance(agent, ProductManagerAgent):
                statement = agent.prioritize_roadmap_rice()
            elif isinstance(agent, UXResearchAgent):
                statement = agent.analyze_ab_test_and_feedback()
            elif isinstance(agent, GrowthHackerAgent):
                statement = agent.analyze_growth_funnel()
            elif isinstance(agent, SalesAgent):
                statement = agent.score_lead_and_playbook()
            elif isinstance(agent, CustomerSuccessAgent):
                statement = agent.predict_churn_and_health()
            else:
                statement = agent.format_decision(
                    "Weekly review complete.", ["Telemetry"], ["Maintain"], "APPROVED", 0.95
                )

            agent_statements.append(statement)

        transcript = {
            "timestamp": datetime.now().isoformat(),
            "meeting_type": "WEEKLY_DEPARTMENT_MEETING",
            "department": department,
            "summary": {"department": department, "agent_count": len(agents), "action": "ROADMAP_ALIGNMENT_APPROVED"},
            "agent_statements": agent_statements,
        }

        json_path = self._save_transcript(f"weekly_{department.lower().replace(' ', '_')}", transcript)
        transcript["transcript_file"] = json_path
        return transcript

    def run_monthly_board_meeting(self) -> Dict[str, Any]:
        """Execute Monthly Board Meeting using LangGraph CEO strategy graph, validator, and red-team critic.

        Returns:
            Dict[str, Any]: Board meeting transcript report.
        """
        cfo_sig = self.cfo.risk_assessment()
        cmo_sig = self.cmo.analyze_gtm_and_campaign()
        coo_sig = self.coo.optimize_supply_chain()
        chro_sig = self.chro.predict_attrition()
        legal_sig = self.legal.analyze_contract()

        initial_state: CEOState = {
            "cfo_signal": cfo_sig,
            "cmo_signal": cmo_sig,
            "coo_signal": coo_sig,
            "chro_signal": chro_sig,
            "legal_signal": legal_sig,
            "risk_score": 0.0,
            "decision": "PENDING",
        }

        graph_output = ceo_app.invoke(initial_state)

        val_report = self.validator.validate_agent_output("CEO Strategy Agent", graph_output)
        critic_report = self.critic.red_team_decision("CEO Strategy Agent", graph_output)

        transcript = {
            "timestamp": datetime.now().isoformat(),
            "meeting_type": "MONTHLY_BOARD_MEETING",
            "department": "CORE C-SUITE & BOARD OF DIRECTORS",
            "summary": {
                "ceo_decision": graph_output.get("decision"),
                "overall_risk_score": graph_output.get("risk_score"),
                "validator_status": val_report["final_decision"]["validation_status"],
                "red_team_flaw_severity": critic_report["final_decision"]["severity"],
            },
            "agent_statements": [cfo_sig, cmo_sig, coo_sig, chro_sig, legal_sig],
            "quality_control": {"validator": val_report, "critic": critic_report},
        }

        json_path = self._save_transcript("monthly_board_meeting", transcript)
        transcript["transcript_file"] = json_path
        return transcript
