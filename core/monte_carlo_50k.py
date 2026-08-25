"""Monte Carlo 50,000 Iteration Risk Engine for PASHA-OS.

Provides Value at Risk (VaR) and Conditional Value at Risk (CVaR) simulations
for portfolio and enterprise risk modeling.
"""

from typing import Tuple
import numpy as np


def run_monte_carlo(
    portfolio_value: float = 1e6,
    mu: float = 0.0005,
    sigma: float = 0.01,
    iterations: int = 50000,
    days: int = 252,
) -> Tuple[float, float, float]:
    """Run a 50,000 iteration Monte Carlo simulation for enterprise VaR & CVaR.

    Args:
        portfolio_value (float): Starting portfolio / asset valuation in USD.
        mu (float): Expected daily return drift rate.
        sigma (float): Expected daily return volatility standard deviation.
        iterations (int): Number of Monte Carlo simulation runs (default 50,000).
        days (int): Time horizon in trading days (default 252).

    Returns:
        Tuple[float, float, float]: (VaR_95, CVaR_95, mean_pnl)
            VaR_95: 95% Value at Risk (dollar amount lost at 5th percentile).
            CVaR_95: 95% Conditional VaR (expected tail loss beyond VaR).
            mean_pnl: Expected mean profit/loss over the horizon.
    """
    np.random.seed(42)
    # Daily simulated price returns using geometric Brownian motion
    daily_returns = np.random.normal(mu, sigma, (iterations, days))
    cum_returns = np.prod(1 + daily_returns, axis=1) - 1.0

    pnl = portfolio_value * cum_returns
    mean_pnl = float(np.mean(pnl))

    # 95% VaR is the 5th percentile loss
    var_95 = float(-np.percentile(pnl, 5))
    tail_losses = pnl[pnl <= -var_95]
    cvar_95 = float(-np.mean(tail_losses)) if len(tail_losses) > 0 else var_95

    return var_95, cvar_95, mean_pnl
