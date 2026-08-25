"""Legal Agent for regulatory compliance, contract analysis, and rule checking."""

from typing import Dict, List, Any


class LegalAgent:
    """Chief Legal Officer & General Counsel Autonomous Agent."""

    def __init__(self) -> None:
        """Initialize Legal Agent with 10 statutory regulatory compliance rules."""
        self.statutory_rules = [
            {"id": "RULE_01", "keywords": ["indemnification", "unlimited liability"], "risk_weight": 0.3},
            {"id": "RULE_02", "keywords": ["gdpr", "data privacy", "pii breach"], "risk_weight": 0.25},
            {"id": "RULE_03", "keywords": ["governing law", "jurisdiction", "offshore"], "risk_weight": 0.15},
            {"id": "RULE_04", "keywords": ["ip assignment", "patent transfer"], "risk_weight": 0.2},
            {"id": "RULE_05", "keywords": ["termination for convenience", "30 days notice"], "risk_weight": 0.1},
            {"id": "RULE_06", "keywords": ["non-compete", "exclusivity"], "risk_weight": 0.2},
            {"id": "RULE_07", "keywords": ["penalty", "liquidated damages"], "risk_weight": 0.25},
            {"id": "RULE_08", "keywords": ["audit rights", "inspection"], "risk_weight": 0.1},
            {"id": "RULE_09", "keywords": ["export control", "sanctions"], "risk_weight": 0.35},
            {"id": "RULE_10", "keywords": ["force majeure", "pandemic"], "risk_weight": 0.1},
        ]

    def analyze_contract(self, text: str = "") -> Dict[str, Any]:
        """Analyze contract text against statutory rules to compute legal risk score.

        Args:
            text (str): Contract string text.

        Returns:
            Dict[str, Any]: Risk score and list of triggered clauses.
        """
        if not text:
            text = (
                "This agreement includes unlimited liability indemnification and "
                "offshore governing law jurisdiction with penalty clauses."
            )

        text_lower = text.lower()
        accumulated_risk = 0.0
        flagged_clauses: List[str] = []

        for rule in self.statutory_rules:
            for kw in rule["keywords"]:
                if kw in text_lower:
                    accumulated_risk += rule["risk_weight"]
                    flagged_clauses.append(f"[{rule['id']}] Triggered keyword: '{kw}'")
                    break

        normalized_risk = min(1.0, round(accumulated_risk, 2))

        return {
            "risk_score": normalized_risk,
            "flagged_clauses": flagged_clauses,
            "compliance_status": "NON_COMPLIANT" if normalized_risk > 0.5 else "COMPLIANT",
        }
