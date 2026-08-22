"""Forensic Audit LLM Agent for FinAgent-Ops."""

import logging
from typing import Any, Dict, List, Optional

from src.models import ForensicRiskEntry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AuditAgent")


class ForensicAuditAgent:
    """Agent executing tool calls and Chain-of-Thought reasoning."""

    def __init__(self, use_llm_mock: bool = True) -> None:
        """Initialize ForensicAuditAgent.

        Args:
            use_llm_mock: If True, uses deterministic CoT reasoning engine.
        """
        self.use_llm_mock = use_llm_mock

    def lookup_vendor_sanction(self, vendor_name: str) -> Dict[str, Any]:
        """Simulate tool calling to check vendor against watchlists.

        Args:
            vendor_name: Name of vendor or entity.

        Returns:
            Dict containing sanction match status and risk flag.
        """
        suspicious_kw = [
            "offshore", "unknown", "shell", "entity x", "wire"
        ]
        v_lower = vendor_name.lower()
        is_suspicious = any(kw in v_lower for kw in suspicious_kw)
        return {
            "vendor": vendor_name,
            "sanction_flag": is_suspicious,
            "risk_score": 0.85 if is_suspicious else 0.05,
            "database_source": "OFAC_MOCK_WATCHLIST",
        }

    def evaluate_discrepancy(
        self,
        discrepancy: Dict[str, Any],
        ledger_ctx: Optional[Dict[str, Any]] = None,
        bank_ctx: Optional[Dict[str, Any]] = None,
    ) -> ForensicRiskEntry:
        """Analyze flagged transaction using tool calls and CoT reflection.

        Args:
            discrepancy: Discrepancy dictionary artifact.
            ledger_ctx: Context ledger transaction dictionary if available.
            bank_ctx: Context bank transaction dictionary if available.

        Returns:
            ForensicRiskEntry schema object.
        """
        disc_id = discrepancy.get("discrepancy_id", "DISC-0000")
        disc_type = discrepancy.get("discrepancy_type", "UNKNOWN")
        amt_diff = float(discrepancy.get("amount_difference", 0.0))
        is_anomaly = bool(discrepancy.get("is_anomaly", False))
        anomaly_score = float(discrepancy.get("anomaly_score", 0.0))

        vendor = ""
        if ledger_ctx:
            vendor = ledger_ctx.get("vendor", "")
        elif bank_ctx:
            vendor = bank_ctx.get("counterparty", "")

        tool_res = self.lookup_vendor_sanction(vendor)

        cot_trace: List[str] = [
            f"[Step 1: Observation] Discrepancy '{disc_id}' ({disc_type}).",
            f"[Step 2: Context] Diff: ${amt_diff:.2f}, Anom: {is_anomaly}.",
            f"[Step 3: Tool] `lookup_vendor_sanction` for '{vendor}'.",
        ]

        risk_level = "Low"
        confidence = 0.95
        root_cause = ""
        action = ""

        is_high_threat = (
            tool_res["sanction_flag"]
            or amt_diff > 50000.0
            or anomaly_score > 0.3
        )
        if is_high_threat:
            risk_level = (
                "Critical"
                if (tool_res["sanction_flag"] and amt_diff > 50000.0)
                else "High"
            )
            cot_trace.append(
                "[Step 4: CoT] High threshold or sanction entity flag."
            )
            root_cause = (
                f"High-risk pattern detected for '{vendor}'. Transaction "
                f"value difference of ${amt_diff:,.2f}."
            )
            action = (
                "Freeze funds, flag transaction for executive AML review, "
                "and initiate SAR filing."
            )

        elif disc_type == "AMOUNT_MISMATCH":
            risk_level = "Medium"
            cot_trace.append(
                "[Step 4: CoT] Amount mismatch for matched reference code."
            )
            root_cause = (
                f"Posting discrepancy or fx fee variance of ${amt_diff:.2f} "
                "for reference transaction."
            )
            action = (
                "Request invoice and bank advice slip from accounts payable "
                "to reconcile differences."
            )

        elif disc_type == "UNMATCHED_LEDGER_ENTRY":
            risk_level = "Low" if amt_diff < 1000.0 else "Medium"
            cot_trace.append(
                f"[Step 4: CoT] Entry for '{vendor}' pending bank clearance."
            )
            root_cause = "Timing difference between ledger and bank clearing."
            action = (
                "Monitor upcoming bank settlement cycles; confirm wire status."
            )

        else:
            risk_level = "Low"
            cot_trace.append(
                "[Step 4: CoT] Minor discrepancy with low statistical risk."
            )
            root_cause = "Unmatched bank charge or petty cash item."
            action = "Assign to junior accountant for routine ledger entry."

        cot_trace.append(f"[Step 5: Conclusion] Risk Level: {risk_level}.")

        return ForensicRiskEntry(
            discrepancy_id=disc_id,
            risk_level=risk_level,
            confidence_score=confidence,
            root_cause_explanation=root_cause,
            recommended_action=action,
            cot_reasoning_trace=cot_trace,
        )

    def process(
        self,
        discrepancies: List[Dict[str, Any]],
        ledger_records: List[Dict[str, Any]],
        bank_records: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Run forensic audit evaluation across all detected discrepancies.

        Args:
            discrepancies: List of discrepancy dicts.
            ledger_records: List of normalized ledger dicts.
            bank_records: List of normalized bank dicts.

        Returns:
            List of ForensicRiskEntry dictionary objects.
        """
        ledger_map = {r["transaction_id"]: r for r in ledger_records}
        bank_map = {r["bank_txn_id"]: r for r in bank_records}

        audit_results: List[Dict[str, Any]] = []

        for disc in discrepancies:
            l_id = disc.get("ledger_txn_id")
            b_id = disc.get("bank_txn_id")

            l_ctx = ledger_map.get(l_id) if l_id else None
            b_ctx = bank_map.get(b_id) if b_id else None

            risk_entry = self.evaluate_discrepancy(disc, l_ctx, b_ctx)
            audit_results.append(risk_entry.model_dump())

        logger.info(
            "Forensic Audit Complete: Evaluated %d discrepancies.",
            len(audit_results),
        )
        return audit_results
