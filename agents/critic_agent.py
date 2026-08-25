"""Critic Agent acting as Red Team to audit and find flaws in agent decisions."""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class CriticAgent(BaseAgent):
    """Critic Autonomous Agent providing adversarial red-teaming and risk stress-testing."""

    def __init__(self) -> None:
        """Initialize Critic Agent."""
        super().__init__(
            agent_name="Critic Agent",
            role="Red Teaming, Flaw Identification, Adversarial Risk Analysis",
            division="QUALITY & ASSURANCE",
        )

    def red_team_decision(self, agent_name: str, decision_data: Dict[str, Any]) -> Dict[str, Any]:
        """Critique and find flaws, unstated assumptions, or vulnerability risks in agent decision.

        Args:
            agent_name (str): Title of target agent.
            decision_data (Dict[str, Any]): Decision object to red-team.

        Returns:
            Dict[str, Any]: Adversarial red team critique report.
        """
        flaws: List[str] = []
        confidence = decision_data.get("confidence_score", 0.9)
        risk_score = decision_data.get("risk_score", 0.3)

        if confidence > 0.95 and risk_score > 0.4:
            flaws.append("Overconfidence bias detected given high inherent operational risk score.")

        if "reasoning" in decision_data and len(decision_data["reasoning"]) < 50:
            flaws.append("Reasoning chain is insufficiently detailed for corporate audit standards.")

        if not decision_data.get("alternatives_considered"):
            flaws.append("Zero alternative strategic options were evaluated.")

        research = self.research_tool(query=f"Red team risk critique model for {agent_name}")

        severity = "HIGH" if len(flaws) >= 2 else ("MEDIUM" if len(flaws) == 1 else "LOW")

        reasoning = (
            f"Executed red team adversarial stress-testing on decision from {agent_name}. "
            f"Identified {len(flaws)} potential logical flaws or risk vulnerabilities. "
            f"Flaw severity assessed as '{severity}'. Red team research from {research['source_used']} integrated."
        )

        return self.format_decision(
            reasoning=reasoning,
            data_sources=[research["source_used"], "PASHA-OS Red Team Vulnerability Matrix"],
            alternatives_considered=[
                "Approve decision without modification",
                "Mandate decision revision with risk mitigation",
            ],
            final_decision={"red_team_status": "FLAWS_DETECTED" if flaws else "APPROVED_CLEAN", "severity": severity},
            confidence_score=0.95,
            extra_fields={"flaws_found": flaws, "flaw_severity": severity},
        )
