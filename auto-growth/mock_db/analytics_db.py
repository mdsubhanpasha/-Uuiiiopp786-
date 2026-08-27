"""
Mock GA4 Analytics Database & SERP Engine for AUTO-GROWTH.
Simulates historical marketing metrics, conversion benchmark data, and SERP keyword competition.
"""

from typing import Dict, Any, List


class MockAnalyticsDB:
    """Mock GA4 & SERP Analytics Database."""

    def __init__(self):
        self._ga4_benchmarks = {
            "SaaS_B2B": {
                "avg_cpc": 4.25,
                "ctr": 0.038,
                "conversion_rate": 0.045,
                "customer_ltv": 1500.0,
                "organic_growth_rate": 0.18,
            },
            "Enterprise_AI": {
                "avg_cpc": 6.50,
                "ctr": 0.042,
                "conversion_rate": 0.052,
                "customer_ltv": 3500.0,
                "organic_growth_rate": 0.22,
            },
            "General_Startup": {
                "avg_cpc": 3.50,
                "ctr": 0.031,
                "conversion_rate": 0.035,
                "customer_ltv": 1200.0,
                "organic_growth_rate": 0.15,
            },
        }

        self._serp_keywords_db = [
            {"keyword": "autonomous ai agents", "search_volume": 12500, "difficulty": 68, "cpc": 5.40},
            {"keyword": "enterprise ai operating system", "search_volume": 8400, "difficulty": 55, "cpc": 7.20},
            {"keyword": "ai marketing automation", "search_volume": 18200, "difficulty": 72, "cpc": 6.10},
            {"keyword": "startup ai workflow software", "search_volume": 9100, "difficulty": 48, "cpc": 4.80},
            {"keyword": "ai agent orchestration platform", "search_volume": 6300, "difficulty": 52, "cpc": 6.90},
            {"keyword": "b2b autonomous growth engine", "search_volume": 4500, "difficulty": 42, "cpc": 5.10},
        ]

    def get_industry_benchmarks(self, category: str = "Enterprise_AI") -> Dict[str, float]:
        """Fetch GA4 historical industry benchmark metrics."""
        return self._ga4_benchmarks.get(category, self._ga4_benchmarks["Enterprise_AI"])

    def get_serp_data(self, keyword_query: str) -> List[Dict[str, Any]]:
        """Fetch SERP search volumes and difficulty scores for target keywords."""
        query_words = keyword_query.lower().split()
        results = []
        for kw_entry in self._serp_keywords_db:
            if any(w in kw_entry["keyword"] for w in query_words) or len(results) < 3:
                results.append(kw_entry)
        return results if results else self._serp_keywords_db[:3]

    def get_historical_campaign_performance(self) -> Dict[str, Any]:
        """Retrieve simulated historical GA4 campaign metrics."""
        return {
            "last_30_days_visitors": 14200,
            "leads_generated": 639,
            "total_spend": 2800.00,
            "revenue": 14500.00,
            "top_performing_channels": [
                {"channel": "Google Search Ads", "roi_multiplier": 3.8, "conversions": 240},
                {"channel": "LinkedIn Content", "roi_multiplier": 4.5, "conversions": 210},
                {"channel": "SEO Blog Organic", "roi_multiplier": 5.2, "conversions": 189},
            ],
        }
