"""
Main AI Log Analyzer orchestrator module for Day 26 - AI Log Analyzer Pro.
Connects parser, anomaly detector, auto-remediator, and Prometheus metrics.
"""

import logging
from typing import Dict, Any, List, Optional
from prometheus_client import Counter, Histogram

from app.log_parser import LogParser
from app.anomaly_detector import AnomalyDetector
from app.auto_remediation import AutoRemediationEngine

logger = logging.getLogger("ai_log_analyzer")

# Prometheus Metrics
LOGS_PARSED_COUNTER = Counter(
    "log_analyzer_logs_parsed_total",
    "Total number of logs parsed",
    ["log_type"]
)

ANOMALIES_DETECTED_COUNTER = Counter(
    "log_analyzer_anomalies_detected_total",
    "Total number of anomalies detected",
    ["anomaly_type", "severity"]
)

REMEDIATIONS_TRIGGERED_COUNTER = Counter(
    "log_analyzer_remediations_triggered_total",
    "Total number of auto-remediations triggered",
    ["action", "status"]
)

ANALYSIS_DURATION = Histogram(
    "log_analyzer_duration_seconds",
    "Duration of log batch analysis"
)


class AILogAnalyzer:
    """Main Orchestrator for parsing logs, detecting anomalies, and triggering remediations."""

    def __init__(self, remediation_script: Optional[str] = None):
        self.parser = LogParser()
        self.detector = AnomalyDetector()
        self.remediator = AutoRemediationEngine(script_path=remediation_script)
        self.anomaly_history: List[Dict[str, Any]] = []

    @ANALYSIS_DURATION.time()
    def process_logs(self, raw_logs: List[str], auto_remediate: bool = True) -> Dict[str, Any]:
        """
        Process a list of log lines.
        1. Parse logs
        2. Update Prometheus parsed counts
        3. Detect anomalies
        4. Trigger remediations if enabled
        5. Return structured analysis summary
        """
        parsed_logs = self.parser.parse_bulk(raw_logs)

        # Update parsed metrics
        for log in parsed_logs:
            ltype = log.get("log_type", "unknown")
            LOGS_PARSED_COUNTER.labels(log_type=ltype).inc()

        # Anomaly Detection
        anomalies = self.detector.detect_anomalies(parsed_logs)

        remediation_results = []
        for anomaly in anomalies:
            atype = anomaly.get("type", "unknown")
            severity = anomaly.get("severity", "INFO")
            ANOMALIES_DETECTED_COUNTER.labels(anomaly_type=atype, severity=severity).inc()

            self.anomaly_history.append(anomaly)

            if auto_remediate and anomaly.get("trigger_remediation"):
                action = anomaly["trigger_remediation"]
                res = self.remediator.remediate_anomaly(anomaly)
                if res:
                    remediation_results.append(res)
                    status = res.get("status", "unknown")
                    REMEDIATIONS_TRIGGERED_COUNTER.labels(action=action, status=status).inc()

        summary = {
            "total_logs_processed": len(parsed_logs),
            "anomalies_found": len(anomalies),
            "anomalies": anomalies,
            "remediations_executed": len(remediation_results),
            "remediations": remediation_results,
            "parsed_logs": parsed_logs[:50]  # Return sample of parsed logs
        }

        return summary

    def get_recent_anomalies(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Return recently recorded anomalies."""
        return self.anomaly_history[-limit:]
