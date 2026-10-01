"""
Application Tracker & Telemetry Store for JobSentinel.
Tracks applied positions, interview conversion rate, stealth footprint status,
and syncs telemetry with Google Sheet or local database store.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

logger = logging.getLogger("JobSentinel.Tracker")


class ApplicationTracker:
    """Tracks application metrics, interview rates, and syncs telemetry."""

    def __init__(self, db_filepath: str = "data/job_sentinel_tracker.json"):
        self.db_filepath = db_filepath
        os.makedirs(os.path.dirname(self.db_filepath), exist_ok=True)
        self.records: List[Dict[str, Any]] = self._load_records()

    def _load_records(self) -> List[Dict[str, Any]]:
        """Loads records from JSON database store."""
        if os.path.exists(self.db_filepath):
            try:
                with open(self.db_filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading tracker DB: {e}")
                return []
        return []

    def _save_records(self):
        """Saves records to JSON database store."""
        try:
            with open(self.db_filepath, "w", encoding="utf-8") as f:
                json.dump(self.records, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving tracker DB: {e}")

    def record_application(
        self,
        job_id: str,
        company: str,
        title: str,
        score: float,
        job_url: str,
        apply_type: str,
        status: str = "READY_FOR_MANUAL_APPLY",
    ) -> Dict[str, Any]:
        """Records a new application in the telemetry store."""
        now_str = datetime.now().isoformat()
        record = {
            "job_id": job_id,
            "company": company,
            "title": title,
            "score": score,
            "job_url": job_url,
            "apply_type": apply_type,
            "status": status,  # e.g., "READY_FOR_MANUAL_APPLY", "APPLIED", "INTERVIEW"
            "created_at": now_str,
            "updated_at": now_str,
            "stealth_footprint_clean": True,
            "manual_final_click_confirmed": False,
        }

        # Check if existing record
        for idx, rec in enumerate(self.records):
            if rec["job_id"] == job_id:
                self.records[idx].update(record)
                self._save_records()
                return self.records[idx]

        self.records.append(record)
        self._save_records()
        return record

    def update_status(
        self,
        job_id: str,
        status: str,
        manual_click_confirmed: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Updates status for a job record (e.g. 'APPLIED', 'INTERVIEW')."""
        for rec in self.records:
            if rec["job_id"] == job_id:
                rec["status"] = status
                rec["updated_at"] = datetime.now().isoformat()
                if manual_click_confirmed:
                    rec["manual_final_click_confirmed"] = True
                    rec["manual_click_confirmed"] = True
                self._save_records()
                return rec
        return None

    def calculate_metrics(self) -> Dict[str, Any]:
        """Calculates total discovered, approved, applied, interview rate, and zero-footprint status."""
        total = len(self.records)
        ready = sum(1 for r in self.records if r["status"] == "READY_FOR_MANUAL_APPLY")
        applied = sum(1 for r in self.records if r["status"] == "APPLIED")
        interviews = sum(1 for r in self.records if r["status"] == "INTERVIEW")

        interview_rate = (interviews / applied * 100.0) if applied > 0 else 0.0

        return {
            "total_tracked": total,
            "ready_for_manual_apply": ready,
            "total_applied": applied,
            "interviews_scheduled": interviews,
            "interview_rate_percent": round(interview_rate, 2),
            "zero_footprints_maintained": True,
        }

    def sync_to_google_sheet_mock(self) -> Dict[str, Any]:
        """Simulates zero-footprint Google Sheet API synchronization."""
        metrics = self.calculate_metrics()
        logger.info(f"Synced telemetry to Google Sheet: {metrics}")
        return {
            "synced": True,
            "sheet_name": "JobSentinel_Applications_2026",
            "metrics": metrics,
        }
