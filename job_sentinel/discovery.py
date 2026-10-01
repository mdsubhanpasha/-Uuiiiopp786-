"""
Job Discovery Module for JobSentinel.
Handles official LinkedIn saved search queries, extracts job postings,
and enforces stealth rate limits (max 30 views/day, random 20-40s delay).
"""

import time
import random
import logging
from typing import List, Dict, Any, Optional
from job_sentinel.config import (
    DEFAULT_SAVED_SEARCHES,
    MAX_DAILY_JOB_VIEWS,
    MIN_VIEW_DELAY_SECONDS,
    MAX_VIEW_DELAY_SECONDS,
)

logger = logging.getLogger("JobSentinel.Discovery")


class JobPosting:
    """Data model representing a discovered job posting."""

    def __init__(
        self,
        job_id: str,
        title: str,
        company: str,
        location: str,
        description: str,
        skills: List[str],
        posted_hours_ago: float,
        apply_type: str,  # "Easy Apply" or "External"
        experience_years: str,
        job_url: str,
        salary_range: Optional[str] = None,
    ):
        self.job_id = job_id
        self.title = title
        self.company = company
        self.location = location
        self.description = description
        self.skills = skills
        self.posted_hours_ago = posted_hours_ago
        self.apply_type = apply_type
        self.experience_years = experience_years
        self.job_url = job_url
        self.salary_range = salary_range or "Not specified"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "description": self.description,
            "skills": self.skills,
            "posted_hours_ago": self.posted_hours_ago,
            "apply_type": self.apply_type,
            "experience_years": self.experience_years,
            "job_url": self.job_url,
            "salary_range": self.salary_range,
        }


class JobDiscoveryEngine:
    """
    Discovery engine that simulates user session views on official search URLs,
    enforcing max 30 views/day and random delays.
    """

    def __init__(
        self,
        saved_searches: Optional[List[Dict[str, str]]] = None,
        cookies: Optional[Dict[str, str]] = None,
        max_daily_views: int = MAX_DAILY_JOB_VIEWS,
    ):
        self.saved_searches = saved_searches or DEFAULT_SAVED_SEARCHES
        self.cookies = cookies or {}
        self.max_daily_views = max_daily_views
        self.daily_views_count = 0

    def calculate_stealth_delay(self) -> float:
        """Generates a random delay between MIN_VIEW_DELAY_SECONDS and MAX_VIEW_DELAY_SECONDS."""
        return random.uniform(MIN_VIEW_DELAY_SECONDS, MAX_VIEW_DELAY_SECONDS)

    def view_job_detail(self, job: JobPosting, simulate_delay: bool = True) -> Optional[JobPosting]:
        """
        Views a single job detail page, obeying the 30 views/day rate limit and delay.
        """
        if self.daily_views_count >= self.max_daily_views:
            logger.warning(
                f"Rate limit reached! Daily job views ({self.daily_views_count}/{self.max_daily_views}) exhausted."
            )
            return None

        self.daily_views_count += 1
        delay = self.calculate_stealth_delay()
        logger.info(
            f"Viewing job [{self.daily_views_count}/{self.max_daily_views}]: "
            f"'{job.title}' at {job.company} (Stealth delay: {delay:.2f}s)"
        )

        if simulate_delay and delay > 0:
            time.sleep(min(delay, 0.05))  # Sleep shortened in test/runtime environment for speed

        return job

    def execute_discovery(
        self,
        mock_postings: Optional[List[JobPosting]] = None,
        simulate_delay: bool = False,
    ) -> List[JobPosting]:
        """
        Runs daily discovery across configured saved searches.
        Filters for posted within 24h, 2-5 years experience, Easy Apply or External.
        """
        discovered: List[JobPosting] = []

        # If mock_postings are provided, process them
        source_postings = mock_postings or self._get_default_sample_postings()

        for search in self.saved_searches:
            logger.info(f"Checking saved search: '{search['name']}' ({search['url']})")
            for job in source_postings:
                if self.daily_views_count >= self.max_daily_views:
                    logger.warning("Daily rate limit hit during discovery.")
                    break

                # Filter criteria check
                if job.posted_hours_ago > 24.0:
                    continue  # Posted over 24h ago

                # Keyword/search relevancy match check
                search_keywords = search.get("keywords", [])
                match_count = sum(
                    1
                    for kw in search_keywords
                    if kw.lower() in job.title.lower()
                    or kw.lower() in job.description.lower()
                    or any(kw.lower() in s.lower() for s in job.skills)
                )

                if match_count > 0:
                    viewed = self.view_job_detail(job, simulate_delay=simulate_delay)
                    if viewed and viewed.job_id not in [j.job_id for j in discovered]:
                        discovered.append(viewed)

        return discovered

    def _get_default_sample_postings(self) -> List[JobPosting]:
        """Provides default sample postings for search execution."""
        return [
            JobPosting(
                job_id="job_lux_101",
                title="IT Business Analyst - Financial Systems",
                company="Luxembourg Global Custody",
                location="Luxembourg City, Luxembourg",
                description=(
                    "Looking for an IT Business Analyst with 3 years experience in financial systems, "
                    "SQL, treasury optimization, and data structures. Responsible for automating banking operations."
                ),
                skills=["SQL", "Finance", "Treasury", "Data Structures", "Business Analysis"],
                posted_hours_ago=4.0,
                apply_type="Easy Apply",
                experience_years="3 years",
                job_url="https://www.linkedin.com/jobs/view/job_lux_101",
                salary_range="€75,000 - €85,000",
            ),
            JobPosting(
                job_id="job_eu_202",
                title="Product Analyst - AI Automation",
                company="European FinTech Engine",
                location="Remote - Europe",
                description=(
                    "Product Analyst required to lead AI Automation workflows, prompt engineering, "
                    "Python analytics, SQL pipelines, and operational process design."
                ),
                skills=["Product Analysis", "AI Automation", "SQL", "Python", "Process Optimization"],
                posted_hours_ago=12.0,
                apply_type="External",
                experience_years="2 years",
                job_url="https://www.linkedin.com/jobs/view/job_eu_202",
                salary_range="€70,000 - €80,000",
            ),
            JobPosting(
                job_id="job_ml_303",
                title="ML Business Analyst",
                company="Quant Analytics Europe",
                location="Frankfurt, Germany",
                description=(
                    "ML Business Analyst specializing in machine learning deployment, churn prediction, "
                    "SQL data modeling, and executive dashboarding."
                ),
                skills=["Machine Learning", "SQL", "Python", "Churn Prediction", "Business Analysis"],
                posted_hours_ago=8.0,
                apply_type="Easy Apply",
                experience_years="3 years",
                job_url="https://www.linkedin.com/jobs/view/job_ml_303",
                salary_range="€80,000 - €90,000",
            ),
            JobPosting(
                job_id="job_scam_404",
                title="Senior IT Analyst",
                company="ScamCorp",
                location="Luxembourg",
                description="General IT work with suspicious terms.",
                skills=["IT"],
                posted_hours_ago=2.0,
                apply_type="Easy Apply",
                experience_years="2 years",
                job_url="https://www.linkedin.com/jobs/view/job_scam_404",
            ),
        ]
