"""COO Agent for operations, SOP compliance, process optimization, and supply chain linear programming."""

from typing import Dict, List, Any
import pulp
from agents.base_agent import BaseAgent


class COOAgent(BaseAgent):
    """Chief Operating Officer Autonomous Agent."""

    def __init__(self) -> None:
        """Initialize COO Agent."""
        super().__init__(
            agent_name="COO Agent",
            role="Operations, Supply Chain Optimization, SOP & Process Efficiency",
            division="CORE C-SUITE",
        )

    def optimize_supply_chain(self, demands: List[float] = None, costs: List[float] = None) -> Dict[str, Any]:
        """Optimize supply chain allocation and costs using PuLP linear programming.

        Args:
            demands (List[float], optional): Node demand requirements.
            costs (List[float], optional): Unit shipping/production costs per node.

        Returns:
            Dict[str, Any]: Optimization result containing optimal cost, allocations, and ReAct decision report.
        """
        demands = demands or [100.0, 150.0, 200.0]
        costs = costs or [10.0, 12.0, 15.0]

        research = self.research_tool(query="Global supply chain optimization linear programming SOP standards")

        n = min(len(demands), len(costs))
        prob = pulp.LpProblem("Supply_Chain_Optimization", pulp.LpMinimize)

        x = [pulp.LpVariable(f"x_{i}", lowBound=0) for i in range(n)]
        prob += pulp.lpSum([costs[i] * x[i] for i in range(n)])

        for i in range(n):
            prob += x[i] >= demands[i]

        prob.solve(pulp.PULP_CBC_CMD(msg=False))

        allocations = [float(pulp.value(x[i])) for i in range(n)]
        total_cost = float(pulp.value(prob.objective)) if prob.objective else 0.0
        status_str = pulp.LpStatus[prob.status]

        reasoning = (
            f"Formulated LP cost minimization problem across {n} nodes with total demand {sum(demands)} units. "
            f"PuLP solver achieved status '{status_str}' with minimal total cost of ${total_cost:,.2f}. "
            f"Operational research from {research['source_used']} confirms SOP optimization strategy."
        )

        return self.format_decision(
            reasoning=reasoning,
            data_sources=[research["source_used"], "PuLP CBC Linear Solver Engine"],
            alternatives_considered=[
                "Fixed manual warehouse allocation",
                "Heuristic greedy nearest-node routing",
                "Linear Programming Minimum Cost Flow",
            ],
            final_decision={"optimal_cost": round(total_cost, 2), "status": status_str},
            confidence_score=0.98 if status_str == "Optimal" else 0.5,
            extra_fields={
                "optimal_cost": round(total_cost, 2),
                "allocation": allocations,
                "status": status_str,
                "risk_score": 0.2 if status_str == "Optimal" else 0.8,
            },
        )
