"""
Ad Agent for AUTO-GROWTH.
Generates high-converting Google Ad copies (Headlines, Descriptions, Keywords)
and computes algorithmic multi-channel budget allocation strategies based on campaign budget.
"""

from typing import Dict, Any, List


class AdAgent:
    """Agent specialized in Google Ad copy generation and multi-channel budget allocation strategy."""

    def __init__(self):
        self.agent_name = "Ad & Growth Budget Specialist"

    def generate_ad_campaign(self, product_name: str, target_audience: str, budget: float) -> Dict[str, Any]:
        """Generates Google Ad copies and calculates optimal channel budget allocation."""
        ad_copies = self._generate_google_ad_copies(product_name, target_audience)
        budget_strategy = self._allocate_budget_strategy(budget)

        return {
            "ad_copies": ad_copies,
            "budget_allocation": budget_strategy,
            "total_budget": budget,
            "ad_variants_generated": len(ad_copies.get("search_ads", [])) + len(ad_copies.get("display_ads", [])),
        }

    def _generate_google_ad_copies(self, product_name: str, target_audience: str) -> Dict[str, List[Dict[str, Any]]]:
        """Creates Google Search & Display Ad copies with headlines, descriptions, and keywords."""
        search_ads = [
            {
                "variant_name": "High-Intent Founder Search",
                "campaign_type": "Google Search - Responsive Search Ad",
                "headlines": [
                    f"{product_name} - AI Marketing",
                    "Replace Your Marketing Team",
                    "5 SEO Blogs + 10 Posts Fast",
                    "Autonomous Growth Engine",
                    "10x Inbound Lead Velocity",
                ],
                "descriptions": [
                    f"Scale {product_name} with autonomous AI agents. Generate research, SEO blogs & ad copy instantly.",
                    f"Stop paying expensive agency retainers. Launch multi-channel campaigns for {target_audience}.",
                ],
                "keywords": [
                    f"+{product_name.lower().replace(' ', ' +')}",
                    "+autonomous +ai +marketing",
                    "+ai +agent +growth",
                    "+b2b +marketing +automation",
                ],
                "target_url": "https://pasha-os.com/auto-growth",
            },
            {
                "variant_name": "Competitor Conquesting",
                "campaign_type": "Google Search - Competitor Keywords",
                "headlines": [
                    "Better Than Traditional Agencies",
                    f"Switch to {product_name}",
                    "AI Agents for Marketing",
                    "Autonomous Campaign Launch",
                ],
                "descriptions": [
                    "Automate market research, SERP SEO optimization, and social content generation in one workflow.",
                    f"Designed specifically for {target_audience} seeking rapid ARR growth.",
                ],
                "keywords": [
                    "marketing agency alternative",
                    "crewai marketing automation",
                    "autogpt enterprise marketing",
                ],
                "target_url": "https://pasha-os.com/compare",
            },
        ]

        display_ads = [
            {
                "banner_size": "1200x628 (Landscape)",
                "headline": f"Replace Your Marketing Agency with {product_name}",
                "description": f"Autonomous AI agents generate blogs, social posts, and ad campaigns for {target_audience}.",
                "cta": "Start Free Trial",
            },
            {
                "banner_size": "1080x1080 (Square / Retargeting)",
                "headline": f"Turn $1,000 Budget into Predictable ARR with {product_name}",
                "description": "閉-loop GA4 analytics, SERP scoring, and 15+ ready-to-publish campaign assets.",
                "cta": "Get Campaign Breakdown",
            },
        ]

        return {"search_ads": search_ads, "display_ads": display_ads}

    def _allocate_budget_strategy(self, budget: float) -> Dict[str, Any]:
        """Calculates algorithmic budget distribution across marketing channels."""
        search_share = 0.50
        linkedin_share = 0.30
        display_share = 0.20

        search_budget = round(budget * search_share, 2)
        linkedin_budget = round(budget * linkedin_share, 2)
        display_budget = round(budget * display_share, 2)

        est_cpc_search = 4.25
        est_cpc_linkedin = 6.50
        est_cpc_display = 1.80

        search_clicks = int(search_budget / est_cpc_search)
        linkedin_clicks = int(linkedin_budget / est_cpc_linkedin)
        display_clicks = int(display_budget / est_cpc_display)

        return {
            "channel_breakdown": [
                {
                    "channel": "Google Search Ads",
                    "allocated_amount": search_budget,
                    "share_percentage": "50%",
                    "est_cpc": est_cpc_search,
                    "est_clicks": search_clicks,
                    "objective": "High-intent keyword conversion",
                },
                {
                    "channel": "LinkedIn Sponsored Content",
                    "allocated_amount": linkedin_budget,
                    "share_percentage": "30%",
                    "est_cpc": est_cpc_linkedin,
                    "est_clicks": linkedin_clicks,
                    "objective": "Target decision maker (CEO/CMO) engagement",
                },
                {
                    "channel": "Google Display & Retargeting",
                    "allocated_amount": display_budget,
                    "share_percentage": "20%",
                    "est_cpc": est_cpc_display,
                    "est_clicks": display_clicks,
                    "objective": "Brand awareness and retargeting website visitors",
                },
            ],
            "total_estimated_clicks": search_clicks + linkedin_clicks + display_clicks,
            "blended_cpc": round(budget / max(search_clicks + linkedin_clicks + display_clicks, 1), 2),
        }
