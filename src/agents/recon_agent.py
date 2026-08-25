"""Reconciliation and Anomaly Detection Agent for FinAgent-Ops."""

import logging
from typing import Any, Dict, List, Set, Tuple

import numpy as np
from sklearn.ensemble import IsolationForest

from src.models import ReconciliationDiscrepancy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReconAgent")


class ReconciliationAgent:
    """Agent for deterministic rule matching & Isolation Forest detection."""

    def __init__(self, contamination: float = 0.15) -> None:
        """Initialize ReconciliationAgent.

        Args:
            contamination: Expected proportion of anomalies in dataset.
        """
        self.contamination = contamination
        self.clf = IsolationForest(
            contamination=self.contamination,
            random_state=42,
        )

    def _extract_features(
        self, records: List[Dict[str, Any]]
    ) -> np.ndarray:
        """Extract numerical feature vectors from financial transactions.

        Args:
            records: List of transaction dictionary objects.

        Returns:
            Numpy 2D array of numerical features.
        """
        features = []
        for r in records:
            amount = float(r.get("amount", 0.0))
            log_amount = np.log1p(abs(amount))
            v_name = str(r.get("vendor", r.get("counterparty", "")))
            vendor_len = float(len(v_name))
            features.append([amount, log_amount, vendor_len])

        if not features:
            return np.zeros((0, 3))
        return np.array(features)

    def detect_anomalies(
        self, records: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Fit Isolation Forest model and identify anomaly transaction records.

        Args:
            records: List of transaction dictionaries.

        Returns:
            Dict mapping ID -> {'is_anomaly': bool, 'anomaly_score': float}.
        """
        if not records:
            return {}

        X = self._extract_features(records)
        if len(records) < 2:
            results = {}
            for r in records:
                id_val = r.get("transaction_id", r.get("bank_txn_id", ""))
                results[id_val] = {"is_anomaly": False, "anomaly_score": 0.0}
            return results

        predictions = self.clf.fit_predict(X)
        scores = self.clf.decision_function(X)

        anomaly_map = {}
        for idx, r in enumerate(records):
            id_val = r.get("transaction_id", r.get("bank_txn_id", ""))
            is_anomaly = bool(predictions[idx] == -1)
            raw_score = float(-scores[idx])
            anomaly_map[id_val] = {
                "is_anomaly": is_anomaly,
                "anomaly_score": round(raw_score, 4),
            }

        return anomaly_map

    def reconcile(
        self,
        ledger_records: List[Dict[str, Any]],
        bank_records: List[Dict[str, Any]],
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Perform deterministic matching and flag statistical anomalies.

        Args:
            ledger_records: List of normalized ledger transaction dicts.
            bank_records: List of normalized bank transaction dicts.

        Returns:
            Tuple of (list of matched records, list of discrepancy dicts).
        """
        matched: List[Dict[str, Any]] = []
        discrepancies: List[Dict[str, Any]] = []

        ledger_anomalies = self.detect_anomalies(ledger_records)
        bank_anomalies = self.detect_anomalies(bank_records)

        matched_bank_ids: Set[str] = set()
        matched_ledger_ids: Set[str] = set()

        ref_bank_map: Dict[str, Dict[str, Any]] = {}
        for b in bank_records:
            ref_code = str(b.get("reference_code", "")).strip()
            if ref_code:
                ref_bank_map[ref_code] = b

        discrepancy_counter = 1

        for l_txn in ledger_records:
            l_id = l_txn["transaction_id"]
            ref_id = str(l_txn.get("reference_id", "")).strip()
            l_amt = float(l_txn["amount"])

            b_match = None
            if ref_id and ref_id in ref_bank_map:
                candidate = ref_bank_map[ref_id]
                b_id = candidate["bank_txn_id"]
                if b_id not in matched_bank_ids:
                    b_match = candidate

            if b_match:
                b_id = b_match["bank_txn_id"]
                b_amt = float(b_match["amount"])
                amt_diff = abs(l_amt - b_amt)

                matched_ledger_ids.add(l_id)
                matched_bank_ids.add(b_id)

                if amt_diff < 0.01:
                    matched.append(
                        {
                            "ledger_txn_id": l_id,
                            "bank_txn_id": b_id,
                            "amount": l_amt,
                            "reference": ref_id,
                            "status": "EXACT_MATCH",
                        }
                    )
                else:
                    l_anom_info = ledger_anomalies.get(
                        l_id, {"is_anomaly": False, "anomaly_score": 0.0}
                    )
                    b_anom_info = bank_anomalies.get(
                        b_id, {"is_anomaly": False, "anomaly_score": 0.0}
                    )
                    is_anom = (
                        l_anom_info["is_anomaly"] or b_anom_info["is_anomaly"]
                    )
                    max_score = max(
                        l_anom_info["anomaly_score"],
                        b_anom_info["anomaly_score"],
                    )

                    disc = ReconciliationDiscrepancy(
                        discrepancy_id=f"DISC-{discrepancy_counter:04d}",
                        ledger_txn_id=l_id,
                        bank_txn_id=b_id,
                        discrepancy_type="AMOUNT_MISMATCH",
                        ledger_amount=l_amt,
                        bank_amount=b_amt,
                        amount_difference=round(amt_diff, 2),
                        is_anomaly=is_anom,
                        anomaly_score=max_score,
                        details=(
                            f"Ref '{ref_id}' matched but amount differs: "
                            f"Ledger=${l_amt:.2f} vs Bank=${b_amt:.2f}"
                        ),
                    )
                    discrepancies.append(disc.model_dump())
                    discrepancy_counter += 1

        for l_txn in ledger_records:
            l_id = l_txn["transaction_id"]
            if l_id not in matched_ledger_ids:
                l_amt = float(l_txn["amount"])
                l_anom_info = ledger_anomalies.get(
                    l_id, {"is_anomaly": False, "anomaly_score": 0.0}
                )

                disc = ReconciliationDiscrepancy(
                    discrepancy_id=f"DISC-{discrepancy_counter:04d}",
                    ledger_txn_id=l_id,
                    bank_txn_id=None,
                    discrepancy_type="UNMATCHED_LEDGER_ENTRY",
                    ledger_amount=l_amt,
                    bank_amount=None,
                    amount_difference=l_amt,
                    is_anomaly=l_anom_info["is_anomaly"],
                    anomaly_score=l_anom_info["anomaly_score"],
                    details=(
                        f"Ledger record {l_id} for vendor "
                        f"'{l_txn.get('vendor')}' amount ${l_amt:.2f} "
                        "has no bank entry."
                    ),
                )
                discrepancies.append(disc.model_dump())
                discrepancy_counter += 1

        for b_txn in bank_records:
            b_id = b_txn["bank_txn_id"]
            if b_id not in matched_bank_ids:
                b_amt = float(b_txn["amount"])
                b_anom_info = bank_anomalies.get(
                    b_id, {"is_anomaly": False, "anomaly_score": 0.0}
                )

                disc = ReconciliationDiscrepancy(
                    discrepancy_id=f"DISC-{discrepancy_counter:04d}",
                    ledger_txn_id=None,
                    bank_txn_id=b_id,
                    discrepancy_type="UNMATCHED_BANK_ENTRY",
                    ledger_amount=None,
                    bank_amount=b_amt,
                    amount_difference=b_amt,
                    is_anomaly=b_anom_info["is_anomaly"],
                    anomaly_score=b_anom_info["anomaly_score"],
                    details=(
                        f"Bank record {b_id} for counterparty "
                        f"'{b_txn.get('counterparty')}' amount ${b_amt:.2f} "
                        "has no ledger entry."
                    ),
                )
                discrepancies.append(disc.model_dump())
                discrepancy_counter += 1

        logger.info(
            "Reconciliation complete: %d matched, %d discrepancies.",
            len(matched),
            len(discrepancies),
        )
        return matched, discrepancies
