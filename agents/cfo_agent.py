"""CFO Agent for financial modeling, cashflow forecasting, runway calculation, and financial risk assessment."""

from typing import Dict, List, Any
import numpy as np


class CFOAgent:
    """Chief Financial Officer Autonomous Agent."""

    def __init__(self, current_balance: float = 5_000_000.0) -> None:
        """Initialize CFO Agent.

        Args:
            current_balance (float): Current liquid cash reserves in USD.
        """
        self.current_balance = current_balance

    def forecast_cashflow(self, historical_data: List[float], months_ahead: int = 12) -> List[float]:
        """Forecast future monthly cashflows based on historical trends.

        Args:
            historical_data (List[float]): Past monthly net cashflow values.
            months_ahead (int): Forecast horizon in months.

        Returns:
            List[float]: Projected cashflows for future months.
        """
        if not historical_data:
            return [100_000.0] * months_ahead

        mean_flow = float(np.mean(historical_data))
        trend = (historical_data[-1] - historical_data[0]) / max(len(historical_data), 1)

        forecasts = []
        for i in range(1, months_ahead + 1):
            projected = mean_flow + (trend * i * 0.1)
            forecasts.append(round(projected, 2))
        return forecasts

    def calculate_runway(self, monthly_burn_rate: float = 250_000.0) -> float:
        """Calculate cash runway in months.

        Args:
            monthly_burn_rate (float): Estimated monthly net burn rate.

        Returns:
            float: Runway length in months.
        """
        if monthly_burn_rate <= 0:
            return 999.0
        return round(self.current_balance / monthly_burn_rate, 2)

    def risk_assessment(self, Historical_cashflows: List[float] = None) -> Dict[str, Any]:
        """Perform financial risk assessment.

        Args:
            Historical_cashflows (List[float], optional): Past cashflows.

        Returns:
            Dict[str, Any]: CFO financial risk assessment dictionary.
        """
        data = Historical_cashflows if Historical_cashflows is not None else [120000, 110000, 95000, 80000]
        forecast = self.forecast_cashflow(data)
        runway = self.calculate_runway(200_000.0)
        risk_score = 0.8 if runway < 12 else 0.25

        return {
            "forecast": forecast,
            "runway_months": runway,
            "risk_score": risk_score,
            "financial_health": "CRITICAL" if risk_score > 0.7 else "HEALTHY",
        }
