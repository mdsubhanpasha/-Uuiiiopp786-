"""
JobSentinel Configuration Module.
Stores configuration parameters for LinkedIn search URLs, stealth rate limits,
scoring thresholds, blocklists, and session parameters.
"""

import os
from typing import List, Dict, Any

DEFAULT_SAVED_SEARCHES: List[Dict[str, str]] = [
    {
        "name": "IT Business Analyst Luxembourg finance",
        "url": "https://www.linkedin.com/jobs/search/?keywords=IT%20Business%20Analyst%20Luxembourg%20finance&f_TPR=r86400&f_E=2%2C3",
        "keywords": ["IT Business Analyst", "finance", "Luxembourg"],
    },
    {
        "name": "Product Analyst AI Automation Europe",
        "url": "https://www.linkedin.com/jobs/search/?keywords=Product%20Analyst%20AI%20Automation%20Europe&f_TPR=r86400&f_E=2%2C3%2C4",
        "keywords": ["Product Analyst", "AI Automation", "Europe"],
    },
    {
        "name": "ML Business Analyst",
        "url": "https://www.linkedin.com/jobs/search/?keywords=ML%20Business%20Analyst&f_TPR=r86400&f_E=2%2C3%2C4",
        "keywords": ["ML Business Analyst", "Machine Learning", "Business Analyst"],
    },
]

# Stealth & Compliance Rate Limits
MAX_DAILY_JOB_VIEWS: int = 30
MIN_VIEW_DELAY_SECONDS: int = 20
MAX_VIEW_DELAY_SECONDS: int = 40

# Zero-Trust Suitability Scoring Thresholds
MIN_SUITABILITY_SCORE: float = 75.0

# Domain, Tech, Experience, and Location Weights (Total = 100%)
WEIGHT_DOMAIN: float = 0.30
WEIGHT_TECH: float = 0.30
WEIGHT_EXPERIENCE: float = 0.20
WEIGHT_LOCATION_SALARY: float = 0.20

# Default Blocklist Companies
DEFAULT_BLOCKLIST_COMPANIES: List[str] = [
    "ScamCorp",
    "FakeTech Ltd",
    "Unscrupulous Staffing",
]

# PII Protection Configuration
HASH_SALT: str = os.getenv("JOBSENTINEL_PII_SALT", "churn_guard_salt_2026")

# Directory Layout
APPLICATIONS_DIR: str = os.getenv("JOBSENTINEL_APPLICATIONS_DIR", "applications")
