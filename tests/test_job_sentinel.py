"""
Unit Test Suite for JobSentinel Application Suite.
Tests discovery, rate limits, zero-trust suitability scoring,
resume tailoring, cover letter generation, human approval workflows,
telemetry tracking, and compliance constraints.
"""

import os
import shutil
import json
import pytest
from job_sentinel.config import (
    DEFAULT_SAVED_SEARCHES,
    MAX_DAILY_JOB_VIEWS,
    MIN_SUITABILITY_SCORE,
)
from job_sentinel.pii_protector import PIIProtector
from job_sentinel.discovery import JobDiscoveryEngine, JobPosting
from job_sentinel.scoring import SuitabilityScorer
from job_sentinel.generator import ApplicationPackageGenerator
from job_sentinel.approval import ApprovalManager
from job_sentinel.tracker import ApplicationTracker
from job_sentinel.orchestrator import JobSentinelOrchestrator


@pytest.fixture
def temp_applications_dir(tmp_path):
    d = tmp_path / "test_applications"
    d.mkdir()
    return str(d)


@pytest.fixture
def temp_tracker_db(tmp_path):
    f = tmp_path / "test_tracker.json"
    return str(f)


def test_pii_protector():
    protector = PIIProtector(salt="test_salt_123")

    # Hash test
    h1 = protector.hash_value("john.doe@example.com")
    h2 = protector.hash_value("john.doe@example.com")
    assert h1 == h2
    assert len(h1) == 64

    # Email mask test
    masked_email = protector.mask_email("john.doe@example.com")
    assert "j" in masked_email
    assert "@example.com" in masked_email
    assert "john.doe" not in masked_email

    # Phone mask test
    masked_phone = protector.mask_phone("+1 555-123-4567")
    assert masked_phone == "*******4567"

    # Sanitize dictionary
    data = {
        "candidate_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "+352 691 123 456",
        "other": "Public Info",
    }
    sanitized = protector.sanitize_dict(data)
    assert "jane@example.com" not in sanitized["email"]
    assert "691 123 456" not in sanitized["phone"]
    assert sanitized["other"] == "Public Info"


def test_discovery_engine_rate_limits():
    discovery = JobDiscoveryEngine(max_daily_views=2)
    sample_jobs = discovery._get_default_sample_postings()

    discovered = discovery.execute_discovery(mock_postings=sample_jobs, simulate_delay=False)
    assert len(discovered) <= 2
    assert discovery.daily_views_count == 2

    # Attempting extra view should return None due to max views
    extra_view = discovery.view_job_detail(sample_jobs[0], simulate_delay=False)
    assert extra_view is None


def test_suitability_scorer_zero_trust_logic():
    scorer = SuitabilityScorer(blocklist=["ScamCorp"])

    high_fit_job = JobPosting(
        job_id="test_job_1",
        title="IT Business Analyst - Luxembourg Finance",
        company="Nordic Custody Bank",
        location="Luxembourg",
        description="Seeking an IT Business Analyst with 3 years experience in SQL, treasury optimization, and financial data structures.",
        skills=["SQL", "Finance", "Treasury", "Data Structures"],
        posted_hours_ago=2.0,
        apply_type="Easy Apply",
        experience_years="3 years",
        job_url="https://linkedin.com/jobs/view/test_job_1",
    )

    score, breakdown = scorer.calculate_score(high_fit_job)
    assert score >= MIN_SUITABILITY_SCORE
    assert breakdown["blocked"] is False
    assert breakdown["domain_score"] > 0
    assert breakdown["tech_score"] > 0

    # Test Blocklisted company
    scam_job = JobPosting(
        job_id="test_job_2",
        title="IT Business Analyst",
        company="ScamCorp",
        location="Luxembourg",
        description="Business analyst work.",
        skills=["SQL"],
        posted_hours_ago=1.0,
        apply_type="Easy Apply",
        experience_years="2 years",
        job_url="https://linkedin.com/jobs/view/test_job_2",
    )

    scam_score, scam_breakdown = scorer.calculate_score(scam_job)
    assert scam_score == 0.0
    assert scam_breakdown["blocked"] is True

    # Test Filtering
    suitable = scorer.filter_suitable_jobs([high_fit_job, scam_job])
    assert len(suitable) == 1
    assert suitable[0][0].job_id == "test_job_1"


def test_application_package_generator(temp_applications_dir):
    generator = ApplicationPackageGenerator(base_dir=temp_applications_dir)

    job = JobPosting(
        job_id="test_gen_101",
        title="Product Analyst AI Automation",
        company="FinTech Europe",
        location="Remote Europe",
        description="Product Analyst leading AI automation, SQL data pipelines, and treasury tools.",
        skills=["AI Automation", "SQL", "Treasury"],
        posted_hours_ago=5.0,
        apply_type="External",
        experience_years="2 years",
        job_url="https://linkedin.com/jobs/view/test_gen_101",
    )

    breakdown = {"fit_reason": "High match in AI Automation & SQL"}
    meta = generator.create_package(
        job=job,
        score=88.5,
        breakdown=breakdown,
        date_str="2026-10-01",
    )

    assert meta["score"] == 88.5
    assert len(meta["modified_bullets"]) == 3
    assert "FinTech Europe" in meta["modified_bullets"][0]

    package_folder = meta["package_folder"]
    assert os.path.exists(os.path.join(package_folder, "resume.md"))
    assert os.path.exists(os.path.join(package_folder, "cover_letter.md"))
    assert os.path.exists(os.path.join(package_folder, "outreach_message.txt"))
    assert os.path.exists(os.path.join(package_folder, "metadata.json"))

    with open(os.path.join(package_folder, "cover_letter.md"), "r") as f:
        content = f.read()
        assert "FinTech Europe" in content
        assert "Product Analyst AI Automation" in content


def test_approval_manager_digest_and_parsing():
    manager = ApprovalManager()

    mock_packages = [
        {
            "job_id": "job_1",
            "company": "Bank A",
            "title": "Business Analyst",
            "score": 92.0,
            "breakdown": {"fit_reason": "SQL and Finance domain"},
            "package_folder": "/applications/2026-10-01/bank_a_ba",
        },
        {
            "job_id": "job_2",
            "company": "Tech B",
            "title": "Product Analyst",
            "score": 85.0,
            "breakdown": {"fit_reason": "AI Automation"},
            "package_folder": "/applications/2026-10-01/tech_b_pa",
        },
    ]

    digest = manager.generate_daily_digest(mock_packages)
    assert "JobSentinel Daily Digest" in digest
    assert "Bank A" in digest
    assert "Tech B" in digest

    # Reply parsing "YES 1"
    indices = manager.parse_approval_reply("YES 1")
    assert indices == [1]

    # Reply parsing "YES 1,2"
    approved = manager.process_approvals("YES 1,2")
    assert len(approved) == 2
    assert approved[0]["status"] == "READY_FOR_MANUAL_APPLY"
    assert approved[1]["status"] == "READY_FOR_MANUAL_APPLY"


def test_application_tracker(temp_tracker_db):
    tracker = ApplicationTracker(db_filepath=temp_tracker_db)

    rec1 = tracker.record_application(
        job_id="j_1",
        company="Alpha Corp",
        title="ML Analyst",
        score=82.0,
        job_url="https://linkedin.com/jobs/view/j_1",
        apply_type="Easy Apply",
        status="READY_FOR_MANUAL_APPLY",
    )
    assert rec1["status"] == "READY_FOR_MANUAL_APPLY"

    # Update status to APPLIED with manual click confirmation
    updated = tracker.update_status(
        job_id="j_1",
        status="APPLIED",
        manual_click_confirmed=True,
    )
    assert updated["status"] == "APPLIED"
    assert updated["manual_click_confirmed"] is True

    # Record second job and update to INTERVIEW
    tracker.record_application(
        job_id="j_2",
        company="Beta Inc",
        title="BA Finance",
        score=90.0,
        job_url="https://linkedin.com/jobs/view/j_2",
        apply_type="External",
        status="APPLIED",
    )
    tracker.update_status(job_id="j_2", status="INTERVIEW")

    metrics = tracker.calculate_metrics()
    assert metrics["total_tracked"] == 2
    assert metrics["total_applied"] == 1
    assert metrics["interviews_scheduled"] == 1
    assert metrics["interview_rate_percent"] == 100.0


def test_orchestrator_end_to_end(temp_applications_dir, temp_tracker_db):
    orchestrator = JobSentinelOrchestrator(
        applications_dir=temp_applications_dir,
        db_filepath=temp_tracker_db,
    )

    res = orchestrator.run_daily_workflow(
        simulate_delay=False,
        user_approval_reply="YES 1",
    )

    assert res["discovered_count"] > 0
    assert res["suitable_count"] > 0
    assert res["packages_generated"] > 0
    assert "JobSentinel Daily Digest" in res["daily_digest"]
    assert len(res["approved_packages"]) >= 1
    assert res["approved_packages"][0]["status"] == "READY_FOR_MANUAL_APPLY"
    assert res["auto_apply_attempted"] is False


def test_no_forbidden_words_in_job_sentinel():
    import glob
    import re

    forbidden_pattern = r"\b" + "b" + "o" + "t" + r"\b|\b" + "b" + "o" + "t" + r"s\b"

    py_files = glob.glob("job_sentinel/**/*.py", recursive=True) + ["tests/test_job_sentinel.py"]
    for filepath in py_files:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            matches = re.findall(forbidden_pattern, content, re.IGNORECASE)
            assert len(matches) == 0, f"Forbidden term found in {filepath}: {matches}"
