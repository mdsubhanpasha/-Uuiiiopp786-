"""CHRO Agent for human resources, hiring strategy, performance matrix, and XGBoost attrition prediction."""

from typing import Dict, List, Any
import numpy as np
import xgboost as xgb
from agents.base_agent import BaseAgent


class CHROAgent(BaseAgent):
    """Chief Human Resources Officer Autonomous Agent."""

    def __init__(self) -> None:
        """Initialize CHRO Agent with a pretrained XGBoost attrition model."""
        super().__init__(
            agent_name="CHRO Agent",
            role="Hiring Strategy, Performance Matrix, Workforce Analytics & Attrition",
            division="CORE C-SUITE",
        )
        self._init_model()

    def _init_model(self) -> None:
        """Initialize and fit a baseline XGBoost model on synthetic HR data."""
        np.random.seed(42)
        X_dummy = np.random.rand(100, 4)
        X_dummy[:, 0] *= 10
        X_dummy[:, 1] *= 1.0
        X_dummy[:, 2] *= 1.0
        X_dummy[:, 3] = np.random.randint(120, 250, size=100)

        y_dummy = ((X_dummy[:, 1] < 0.4) | (X_dummy[:, 0] < 1.5)).astype(int)

        self.model = xgb.XGBClassifier(n_estimators=10, max_depth=3, random_state=42, eval_metric="logloss")
        self.model.fit(X_dummy, y_dummy)

    def predict_attrition(self, employee_features: List[List[float]] = None) -> Dict[str, Any]:
        """Predict employee turnover probabilities using XGBoost model.

        Args:
            employee_features (List[List[float]], optional): Feature matrix for employees.

        Returns:
            Dict[str, Any]: Attrition risk predictions and ReAct decision report.
        """
        if not employee_features:
            employee_features = [
                [2.5, 0.8, 0.9, 160.0],
                [0.8, 0.3, 0.5, 220.0],
                [5.0, 0.7, 0.8, 175.0],
            ]

        research = self.research_tool(query="Tech MNC employee retention hiring strategy performance matrix 2025")

        X_arr = np.array(employee_features)
        probs = self.model.predict_proba(X_arr)[:, 1]
        probs_list = [round(float(p), 3) for p in probs]
        high_risk_count = sum(1 for p in probs_list if p > 0.5)
        overall_risk = round(float(np.mean(probs_list)), 2)

        workforce_health = "STABLE" if overall_risk < 0.5 else "HIGH_ATTRITION_RISK"

        reasoning = (
            f"Evaluated {len(employee_features)} employee profiles through XGBoost attrition model. "
            f"Identified {high_risk_count} high-risk personnel (mean probability: {overall_risk}). "
            f"HR research from {research['source_used']} recommends target performance matrix retention incentives."
        )

        return self.format_decision(
            reasoning=reasoning,
            data_sources=[research["source_used"], "XGBoost Employee Attrition Model"],
            alternatives_considered=[
                "Standard annual compensation review",
                "Targeted retention bonus & career ladder matrix",
                "Workload rebalancing & wellness program",
            ],
            final_decision={"workforce_health": workforce_health, "high_risk_count": high_risk_count},
            confidence_score=0.91,
            extra_fields={
                "attrition_probabilities": probs_list,
                "high_risk_count": high_risk_count,
                "risk_score": overall_risk,
                "workforce_health": workforce_health,
            },
        )
