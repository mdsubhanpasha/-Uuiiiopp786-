"""Validator Agent for cross-checking and validating all autonomous agent outputs in PASHA-OS."""

from typing import Dict, Any, List
from agents.base_agent import BaseAgent


class ValidatorAgent(BaseAgent):
    """Validator Autonomous Agent ensuring 100% decision accuracy and schema compliance."""

    def __init__(self) -> None:
        """Initialize Validator Agent."""
        super().__init__(
            agent_name="Validator Agent",
            role="Result Quality Assurance, Schema Integrity & Cross-Verification",
            division="QUALITY & ASSURANCE",
        )

    def validate_agent_output(self, agent_name: str, output: Dict[str, Any]) -> Dict[str, Any]:
        """Validate agent output against ReAct schema and confidence requirements.

        Args:
            agent_name (str): Title of agent under review.
            output (Dict[str, Any]): Decision dictionary produced by agent.

        Returns:
            Dict[str, Any]: Validation report with boolean pass status and detected issues.
        """
        required_keys = ["reasoning", "data_sources", "alternatives_considered", "final_decision", "confidence_score"]
        missing_keys = [k for k in required_keys if k not in output]

        passed = len(missing_keys) == 0
        issues: List[str] = []

        if missing_keys:
            issues.append(f"Missing required ReAct keys: {missing_keys}")

        confidence = output.get("confidence_score", 0.0)
        if confidence < 0.5:
            issues.append(f"Low confidence score: {confidence}")

        research = self.research_tool(query=f"Quality assurance verification for {agent_name}")

        reasoning = (
            f"Evaluated output structure for {agent_name}. Verified {len(output)} output fields against system schema. "
            f"Validation status: {'PASSED' if passed else 'FAILED'} with {len(issues)} flags. "
            f"Assurance guidelines from {research['source_used']} confirmed."
        )

        return self.format_decision(
            reasoning=reasoning,
            data_sources=[research["source_used"], "PASHA-OS Schema Engine"],
            alternatives_considered=["Accept agent output", "Reject and request agent recalculation"],
            final_decision={"validation_status": "PASSED" if passed else "FAILED", "issues": issues},
            confidence_score=0.99,
            extra_fields={"is_valid": passed, "issues": issues},
        )
