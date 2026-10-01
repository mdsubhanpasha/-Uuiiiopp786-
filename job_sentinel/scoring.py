"""
Suitability Scoring Module for JobSentinel.
Implements ChurnGuard Zero-Trust Logic to evaluate job postings on a 0-100 scale:
- Domain match (finance, ops, treasury) = 30%
- Tech match (SQL, data structures, AI tools) = 30%
- Experience match (2-3 years) = 20%
- Location/salary match = 20%
Only jobs scoring >75% and not on the blocklist are passed to package generation.
"""

import re
import logging
from typing import List, Dict, Any, Tuple
from job_sentinel.config import (
    MIN_SUITABILITY_SCORE,
    WEIGHT_DOMAIN,
    WEIGHT_TECH,
    WEIGHT_EXPERIENCE,
    WEIGHT_LOCATION_SALARY,
    DEFAULT_BLOCKLIST_COMPANIES,
)
from job_sentinel.discovery import JobPosting

logger = logging.getLogger("JobSentinel.Scoring")


class SuitabilityScorer:
    """Zero-trust suitability scoring engine for job relevance evaluation."""

    def __init__(self, blocklist: List[str] = None):
        self.blocklist = [b.lower() for b in (blocklist or DEFAULT_BLOCKLIST_COMPANIES)]

        # Keyword sets
        self.domain_keywords = [
            "finance",
            "treasury",
            "ops",
            "operations",
            "custody",
            "banking",
            "fintech",
            "automation",
        ]
        self.tech_keywords = [
            "sql",
            "data structures",
            "ai tools",
            "python",
            "ai",
            "machine learning",
            "data modeling",
            "prompt engineering",
        ]
        self.target_experience_years = [2, 3, 4, 5]
        self.preferred_locations = ["luxembourg", "europe", "remote", "germany", "france"]

    def is_company_blocked(self, company_name: str) -> bool:
        """Checks if the company is in the blocklist."""
        company_lower = company_name.lower().strip()
        return any(blocked in company_lower for blocked in self.blocklist)

    def calculate_score(self, job: JobPosting) -> Tuple[float, Dict[str, Any]]:
        """
        Calculates 0-100 score based on 4 weighted categories.
        Returns total_score and component breakdown.
        """
        if self.is_company_blocked(job.company):
            logger.info(f"Job '{job.title}' at '{job.company}' BLOCKED by company blocklist.")
            return 0.0, {
                "blocked": True,
                "reason": f"Company '{job.company}' is in blocklist.",
                "total_score": 0.0,
            }

        text_corpus = f"{job.title} {job.description} {' '.join(job.skills)}".lower()

        # 1. Domain Match Score (30%)
        domain_matches = sum(1 for kw in self.domain_keywords if kw in text_corpus)
        domain_score = min(100.0, (domain_matches / 3.0) * 100.0)

        # 2. Tech Match Score (30%)
        tech_matches = sum(1 for kw in self.tech_keywords if kw in text_corpus)
        tech_score = min(100.0, (tech_matches / 3.0) * 100.0)

        # 3. Experience Match Score (20%)
        # Look for 2-5 years experience mentioned or matching experience field
        exp_score = 50.0
        exp_digits = [int(d) for d in re.findall(r"\b([2-5])\b", job.experience_years + " " + job.description)]
        if exp_digits and any(e in self.target_experience_years for e in exp_digits):
            exp_score = 100.0
        elif "2-5" in job.description or "2 to 5" in job.description or "3+" in job.description:
            exp_score = 100.0

        # 4. Location / Salary Match Score (20%)
        loc_score = 50.0
        if any(loc in job.location.lower() for loc in self.preferred_locations):
            loc_score = 100.0

        # Weighted Total Calculation
        total_score = (
            (domain_score * WEIGHT_DOMAIN)
            + (tech_score * WEIGHT_TECH)
            + (exp_score * WEIGHT_EXPERIENCE)
            + (loc_score * WEIGHT_LOCATION_SALARY)
        )

        breakdown = {
            "blocked": False,
            "domain_score": round(domain_score, 1),
            "tech_score": round(tech_score, 1),
            "experience_score": round(exp_score, 1),
            "location_score": round(loc_score, 1),
            "total_score": round(total_score, 1),
            "fit_reason": (
                f"Domain match ({domain_matches} keywords), "
                f"Tech match ({tech_matches} keywords), "
                f"Experience ({job.experience_years}), Location ({job.location})"
            ),
        }

        return round(total_score, 1), breakdown

    def filter_suitable_jobs(
        self,
        postings: List[JobPosting],
        min_threshold: float = MIN_SUITABILITY_SCORE,
    ) -> List[Tuple[JobPosting, float, Dict[str, Any]]]:
        """
        Filters job postings keeping only those scoring > min_threshold and not blocked.
        """
        suitable: List[Tuple[JobPosting, float, Dict[str, Any]]] = []
        for job in postings:
            score, breakdown = self.calculate_score(job)
            if not breakdown.get("blocked", False) and score > min_threshold:
                suitable.append((job, score, breakdown))
                logger.info(f"ACCEPTED: '{job.title}' at {job.company} - Score: {score}%")
            else:
                logger.info(
                    f"REJECTED: '{job.title}' at {job.company} - Score: {score}% (Threshold: >{min_threshold}%)"
                )

        # Sort descending by score
        suitable.sort(key=lambda x: x[1], reverse=True)
        return suitable
