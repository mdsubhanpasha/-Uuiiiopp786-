"""CHRO Agent for human resources, workforce analytics, and XGBoost attrition prediction."""

from typing import Dict, List, Any
import numpy as np
import xgboost as xgb


class CHROAgent:
    """Chief Human Resources Officer Autonomous Agent."""

    def __init__(self) -> None:
        """Initialize CHRO Agent with a pretrained dummy XGBoost attrition model."""
        self._init_model()

    def _init_model(self) -> None:
        """Initialize and fit a baseline XGBoost model on synthetic HR data."""
        np.random.seed(42)
        # Synthetic features: [tenure_years, satisfaction_score, last_evaluation, monthly_hours]
        X_dummy = np.random.rand(100, 4)
        X_dummy[:, 0] *= 10  # Tenure 0-10 years
        X_dummy[:, 1] *= 1.0  # Satisfaction 0-1
        X_dummy[:, 2] *= 1.0  # Evaluation 0-1
        X_dummy[:, 3] = np.random.randint(120, 250, size=100)

        # High attrition if satisfaction is low (< 0.4) or tenure is low (< 2)
        y_dummy = ((X_dummy[:, 1] < 0.4) | (X_dummy[:, 0] < 1.5)).astype(int)

        self.model = xgb.XGBClassifier(n_estimators=10, max_depth=3, random_state=42, eval_metric="logloss")
        self.model.fit(X_dummy, y_dummy)

    def predict_attrition(self, employee_features: List[List[float]] = None) -> Dict[str, Any]:
        """Predict employee turnover probabilities using XGBoost model.

        Args:
            employee_features (List[List[float]], optional): Feature matrix for employees.

        Returns:
            Dict[str, Any]: Attrition risk predictions and high-risk count.
        """
        if not employee_features:
            # Default 3 sample employee feature vectors
            employee_features = [
                [2.5, 0.8, 0.9, 160.0],  # Low risk
                [0.8, 0.3, 0.5, 220.0],  # High risk
                [5.0, 0.7, 0.8, 175.0],  # Low risk
            ]

        X_arr = np.array(employee_features)
        probs = self.model.predict_proba(X_arr)[:, 1]
        probs_list = [round(float(p), 3) for p in probs]
        high_risk_count = sum(1 for p in probs_list if p > 0.5)
        overall_risk = round(float(np.mean(probs_list)), 2)

        return {
            "attrition_probabilities": probs_list,
            "high_risk_count": high_risk_count,
            "risk_score": overall_risk,
            "workforce_health": "STABLE" if overall_risk < 0.5 else "HIGH_ATTRITION_RISK",
        }
