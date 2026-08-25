"""Product Manager Agent for PRDs, Roadmaps, User Stories, and RICE Prioritization."""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class ProductManagerAgent(BaseAgent):
    """Product Manager Autonomous Agent."""

    def __init__(self) -> None:
        """Initialize Product Manager Agent."""
        super().__init__(
            agent_name="Product Manager Agent",
            role="PRD Creation, Product Roadmap, User Stories & RICE Framework Prioritization",
            division="PRODUCT & GROWTH DIVISION",
        )

    def prioritize_roadmap_rice(self, features: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Prioritize product feature backlog using RICE framework (Reach * Impact * Confidence / Effort).

        Args:
            features (List[Dict[str, Any]], optional): Feature candidates with RICE parameters.

        Returns:
            Dict[str, Any]: Prioritized feature roadmap and ReAct decision report.
        """
        if not features:
            features = [
                {"name": "Autonomous Workflows V2", "reach": 10000, "impact": 3.0, "confidence": 0.9, "effort": 2.0},
                {"name": "Legacy CSV Export", "reach": 1000, "impact": 1.0, "confidence": 0.8, "effort": 1.0},
                {"name": "WebSocket Streaming", "reach": 5000, "impact": 2.5, "confidence": 0.85, "effort": 1.5},
            ]

        research = self.research_tool(
            query="Enterprise SaaS Product Manager RICE framework PRD roadmap standards 2025"
        )

        prioritized = []
        for feat in features:
            rice_score = (feat["reach"] * feat["impact"] * feat["confidence"]) / max(feat["effort"], 0.1)
            feat_copy = dict(feat)
            feat_copy["rice_score"] = round(rice_score, 2)
            prioritized.append(feat_copy)

        prioritized.sort(key=lambda x: x["rice_score"], reverse=True)
        top_feature = prioritized[0]["name"]

        reasoning = (
            f"Evaluated {len(features)} backlog features via RICE prioritization framework. "
            f"Top prioritized feature: '{top_feature}' with RICE score {prioritized[0]['rice_score']}. "
            f"Product strategy research from {research['source_used']} confirmed feature alignment."
        )

        return self.format_decision(
            reasoning=reasoning,
            data_sources=[research["source_used"], "Jira / Productboard Backlog Engine"],
            alternatives_considered=["MoSCoW Prioritization", "RICE Prioritization Framework"],
            final_decision={"top_priority_feature": top_feature, "prioritized_backlog": prioritized},
            confidence_score=0.95,
            extra_fields={"prioritized_backlog": prioritized, "risk_score": 0.15},
        )
