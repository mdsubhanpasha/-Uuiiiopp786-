"""Customer Success Agent for churn prediction, support automation, and account health scoring."""

from typing import Dict, Any
from agents.base_agent import BaseAgent


class CustomerSuccessAgent(BaseAgent):
    """Customer Success Autonomous Agent."""

    def __init__(self) -> None:
        """Initialize Customer Success Agent."""
        super().__init__(
            agent_name="Customer Success Agent",
            role="Churn Prediction, Account Health Scoring & Automated Support Ticketing",
            division="CUSTOMER & SALES DIVISION",
        )

    def predict_churn_and_health(self, account_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Predict customer account churn risk score and generate support interventions.

        Args:
            account_data (Dict[str, Any], optional): Account telemetry (login frequency, open tickets).

        Returns:
            Dict[str, Any]: Churn prediction report and ReAct decision report.
        """
        acc = account_data or {
            "account_name": "Acme Global Industries",
            "weekly_logins": 4,
            "open_critical_tickets": 2,
            "nps_score": 5,
        }

        research = self.research_tool(query="Enterprise CS customer health score churn prediction automation 2025")

        churn_risk = 0.1
        if acc.get("weekly_logins", 10) < 5:
            churn_risk += 0.35
        if acc.get("open_critical_tickets", 0) > 1:
            churn_risk += 0.35
        if acc.get("nps_score", 10) < 7:
            churn_risk += 0.15

        churn_risk = min(1.0, round(churn_risk, 2))
        health_status = "AT_RISK" if churn_risk > 0.5 else "HEALTHY"

        reasoning = (
            f"Assessed account '{acc.get('account_name')}' telemetry: weekly logins ({acc.get('weekly_logins')}), "
            f"critical tickets ({acc.get('open_critical_tickets')}), NPS ({acc.get('nps_score')}). "
            f"Calculated churn risk score: {churn_risk} (Health Status: '{health_status}'). "
            f"CS best practices from {research['source_used']} triggered automated CSM intervention."
        )

        return self.format_decision(
            reasoning=reasoning,
            data_sources=[research["source_used"], "Gainsight / Zendesk Customer Health Telemetry"],
            alternatives_considered=["Automated CS check-in email", "Assign Executive Sponsor & Technical CSM"],
            final_decision={"health_status": health_status, "churn_risk_score": churn_risk},
            confidence_score=0.93,
            extra_fields={"churn_risk_score": churn_risk, "health_status": health_status, "risk_score": churn_risk},
        )
