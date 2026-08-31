"""
ML and Regex based Anomaly Detector for Day 26 - AI Log Analyzer Pro.
Uses IsolationForest from scikit-learn alongside pattern detection for 5xx spikes, OOM, and CrashLoopBackOff.
"""

import re
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from sklearn.ensemble import IsolationForest


class AnomalyDetector:
    """Anomaly detection combining Isolation Forest ML model and pattern heuristics."""

    CRITICAL_PATTERNS = {
        "DISK_FULL": re.compile(r"disk\s*full|no\s*space\s*left\s*on\s*device|out\s*of\s*disk\s*space", re.IGNORECASE),
        "OOM_KILLED": re.compile(r"oom|oomkilled|out\s*of\s*memory|memory\s*limit\s*exceeded", re.IGNORECASE),
        "CRASH_LOOP": re.compile(r"crashloopbackoff|back-off\s*restarting\s*failed\s*container|pod\s*crashed", re.IGNORECASE),
        "HIGH_5XX_SPIKE": re.compile(r"5xx\s*spike|5\d{2}\s*server\s*error|500\s*internal\s*server\s*error|502\s*bad\s*gateway|503\s*service\s*unavailable", re.IGNORECASE),
    }

    def __init__(self, contamination: float = 0.1):
        """Initialize IsolationForest model."""
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42
        )
        self.is_fitted = False

    def _extract_features(self, parsed_logs: List[Dict[str, Any]]) -> np.ndarray:
        """Extract numerical feature matrix for IsolationForest model."""
        features = []
        for log in parsed_logs:
            msg = str(log.get("message", ""))
            status = float(log.get("status_code", 200))
            is_err = 1.0 if log.get("is_error", False) else 0.0
            is_5xx = 1.0 if log.get("is_5xx", False) else 0.0
            msg_len = float(len(msg))
            has_critical_kw = 1.0 if any(pat.search(msg) for pat in self.CRITICAL_PATTERNS.values()) else 0.0

            features.append([status, is_err, is_5xx, msg_len, has_critical_kw])

        return np.array(features, dtype=np.float64)

    def fit_model(self, parsed_logs: List[Dict[str, Any]]) -> None:
        """Fit IsolationForest on a baseline set of logs."""
        if not parsed_logs:
            return
        X = self._extract_features(parsed_logs)
        self.model.fit(X)
        self.is_fitted = True

    def detect_anomalies(self, parsed_logs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect anomalies using pattern matching and IsolationForest ML model."""
        if not parsed_logs:
            return []

        anomalies = []

        # 1. Calculate rate-based metrics across batch
        count_5xx = sum(1 for log in parsed_logs if log.get("is_5xx", False) or "500" in str(log.get("message", "")))
        total_logs = len(parsed_logs)
        has_5xx_spike = count_5xx >= 10 or (total_logs > 0 and (count_5xx / total_logs) >= 0.3)

        if has_5xx_spike:
            anomalies.append({
                "type": "5xx_spike",
                "severity": "CRITICAL",
                "confidence_score": 0.95,
                "message": f"Detected 5xx HTTP Error Spike: {count_5xx} 5xx errors encountered in batch.",
                "count_5xx": count_5xx,
                "trigger_remediation": "scale_up",
            })

        # 2. Extract features and fit model if not fitted
        X = self._extract_features(parsed_logs)
        if not self.is_fitted and len(X) >= 5:
            self.fit_model(parsed_logs)

        ml_scores = []
        if self.is_fitted:
            # -1 represents anomaly in IsolationForest
            ml_predictions = self.model.predict(X)
            ml_scores = self.model.decision_function(X)
        else:
            ml_predictions = np.ones(len(parsed_logs))

        # 3. Rule-based and ML anomaly evaluation per log entry
        for idx, (log, is_ml_anomaly) in enumerate(zip(parsed_logs, ml_predictions)):
            msg = str(log.get("message", ""))

            # Check explicit pattern matches
            if self.CRITICAL_PATTERNS["DISK_FULL"].search(msg):
                anomalies.append({
                    "type": "disk_full",
                    "severity": "CRITICAL",
                    "confidence_score": 0.99,
                    "message": f"Disk Full anomaly detected: {msg}",
                    "log_entry": log,
                    "trigger_remediation": "cleanup",
                })
            elif self.CRITICAL_PATTERNS["OOM_KILLED"].search(msg):
                anomalies.append({
                    "type": "oom_killed",
                    "severity": "CRITICAL",
                    "confidence_score": 0.98,
                    "message": f"Out Of Memory (OOM) anomaly detected: {msg}",
                    "log_entry": log,
                    "trigger_remediation": "restart_pod",
                })
            elif self.CRITICAL_PATTERNS["CRASH_LOOP"].search(msg):
                anomalies.append({
                    "type": "crash_loop_backoff",
                    "severity": "CRITICAL",
                    "confidence_score": 0.98,
                    "message": f"CrashLoopBackOff anomaly detected: {msg}",
                    "log_entry": log,
                    "trigger_remediation": "restart_pod",
                })
            elif is_ml_anomaly == -1 and log.get("is_error", False):
                score = float(ml_scores[idx]) if len(ml_scores) > idx else -0.5
                conf = round(min(0.95, max(0.60, abs(score) + 0.5)), 2)
                anomalies.append({
                    "type": "ml_behavioral_anomaly",
                    "severity": "HIGH",
                    "confidence_score": conf,
                    "message": f"ML IsolationForest detected unexpected log behavior: {msg[:120]}",
                    "log_entry": log,
                    "trigger_remediation": None,
                })

        return anomalies
