"""
Main Orchestrator for JobSentinel Application Suite.
Coordinates the end-to-end daily workflow:
1. 9:00 AM Discovery (Saved LinkedIn searches, stealth rate limits)
2. Suitability Scoring (Zero-Trust ChurnGuard logic, >75% threshold)
3. Application Package Generation (Tailored resume, cover letter, outreach message)
4. 10:00 AM Daily Digest & Human Approval (Parses 'YES 1,3' response, manual submission enforcement)
5. Telemetry Tracking & Google Sheet sync.
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

from job_sentinel.config import MAX_DAILY_JOB_VIEWS
from job_sentinel.pii_protector import PIIProtector
from job_sentinel.discovery import JobDiscoveryEngine, JobPosting
from job_sentinel.scoring import SuitabilityScorer
from job_sentinel.generator import ApplicationPackageGenerator
from job_sentinel.approval import ApprovalManager
from job_sentinel.tracker import ApplicationTracker

logger = logging.getLogger("JobSentinel.Orchestrator")


class JobSentinelOrchestrator:
    """Master orchestrator for the JobSentinel agent system."""

    def __init__(
        self,
        blocklist: Optional[List[str]] = None,
        db_filepath: str = "data/job_sentinel_tracker.json",
        applications_dir: str = "applications",
    ):
        self.pii_protector = PIIProtector()
        self.discovery_engine = JobDiscoveryEngine()
        self.scorer = SuitabilityScorer(blocklist=blocklist)
        self.generator = ApplicationPackageGenerator(base_dir=applications_dir)
        self.approval_manager = ApprovalManager()
        self.tracker = ApplicationTracker(db_filepath=db_filepath)

    def run_daily_workflow(
        self,
        mock_postings: Optional[List[JobPosting]] = None,
        simulate_delay: bool = False,
        user_approval_reply: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes the full daily workflow.
        Returns complete workflow outcome including digest, packages, and telemetry.
        """
        date_str = datetime.now().strftime("%Y-%m-%d")
        logger.info(f"=== Starting JobSentinel Daily Workflow for {date_str} ===")

        # 1. DISCOVERY (9:00 AM)
        discovered_jobs = self.discovery_engine.execute_discovery(
            mock_postings=mock_postings,
            simulate_delay=simulate_delay,
        )
        logger.info(f"Discovered {len(discovered_jobs)} matching job postings within last 24h.")

        # 2. SUITABILITY SCORING (Zero-Trust ChurnGuard Logic)
        suitable_jobs = self.scorer.filter_suitable_jobs(discovered_jobs, min_threshold=75.0)
        logger.info(f"Identified {len(suitable_jobs)} jobs meeting >75% suitability threshold.")

        # 3. APPLICATION PACKAGE GENERATION
        generated_packages: List[Dict[str, Any]] = []
        for job, score, breakdown in suitable_jobs:
            package_meta = self.generator.create_package(
                job=job,
                score=score,
                breakdown=breakdown,
                date_str=date_str,
            )
            generated_packages.append(package_meta)

            # Record in tracker
            self.tracker.record_application(
                job_id=job.job_id,
                company=job.company,
                title=job.title,
                score=score,
                job_url=job.job_url,
                apply_type=job.apply_type,
                status="DRAFTED_PENDING_APPROVAL",
            )

        # 4. HUMAN APPROVAL (10:00 AM Digest)
        digest_text = self.approval_manager.generate_daily_digest(
            scored_packages=generated_packages,
            top_k=5,
        )

        approved_packages: List[Dict[str, Any]] = []
        if user_approval_reply:
            approved_packages = self.approval_manager.process_approvals(user_approval_reply)
            for approved in approved_packages:
                self.tracker.update_status(
                    job_id=approved["job_id"],
                    status="READY_FOR_MANUAL_APPLY",
                    manual_click_confirmed=False,  # Enforces manual click required
                )

        # 5. TELEMETRY & REPORTING
        metrics = self.tracker.calculate_metrics()
        self.tracker.sync_to_google_sheet_mock()

        return {
            "date": date_str,
            "discovered_count": len(discovered_jobs),
            "suitable_count": len(suitable_jobs),
            "packages_generated": len(generated_packages),
            "daily_digest": digest_text,
            "approved_packages": approved_packages,
            "telemetry_metrics": metrics,
            "auto_apply_attempted": False,  # MUST be False
        }
