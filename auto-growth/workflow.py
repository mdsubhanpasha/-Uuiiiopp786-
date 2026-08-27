"""
Autonomous Marketing Workflow Orchestrator for AUTO-GROWTH.
Coordinates 5 CrewAI/LangGraph style agents sequentially:
Market Research -> Content Generation -> SEO Optimization -> Ad Campaign & Budget Allocation -> Analytics & ROI Projection.
Saves all generated deliverables into /auto-growth/outputs/.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

try:
    from agents.market_research_agent import MarketResearchAgent
    from agents.content_agent import ContentAgent
    from agents.seo_agent import SEOAgent
    from agents.ad_agent import AdAgent
    from agents.analytics_agent import AnalyticsAgent
except ImportError:
    from auto_growth.agents.market_research_agent import MarketResearchAgent
    from auto_growth.agents.content_agent import ContentAgent
    from auto_growth.agents.seo_agent import SEOAgent
    from auto_growth.agents.ad_agent import AdAgent
    from auto_growth.agents.analytics_agent import AnalyticsAgent

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("AutonomousMarketingWorkflow")


class AutonomousMarketingWorkflow:
    """Orchestrates end-to-end multi-agent autonomous growth marketing campaign pipeline."""

    def __init__(
        self,
        tavily_api_key: Optional[str] = None,
        perplexity_api_key: Optional[str] = None,
        openai_api_key: Optional[str] = None,
        serp_api_key: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = output_dir or os.path.join(base_dir, "outputs")
        os.makedirs(self.output_dir, exist_ok=True)

        self.research_agent = MarketResearchAgent(tavily_api_key=tavily_api_key, perplexity_api_key=perplexity_api_key)
        self.content_agent = ContentAgent(openai_api_key=openai_api_key)
        self.seo_agent = SEOAgent(serp_api_key=serp_api_key)
        self.ad_agent = AdAgent()
        self.analytics_agent = AnalyticsAgent()

    def run_campaign(
        self,
        product_name: str = "PASHA-OS",
        target_audience: str = "US startups",
        budget: float = 1000.0,
    ) -> Dict[str, Any]:
        """Executes full multi-agent campaign pipeline autonomously."""
        logger.info(f"🚀 Starting AUTO-GROWTH Campaign for '{product_name}' (Target: '{target_audience}', Budget: ${budget:,.2f})")

        # Step 1: Market Research Agent
        logger.info("Agent 1/5 [Market Research Agent]: Researching competitors & buyer personas...")
        market_insights = self.research_agent.research(product_name=product_name, target_audience=target_audience)

        # Step 2: Content Agent
        logger.info("Agent 2/5 [Content Agent]: Generating 5 SEO blogs, 10 LinkedIn posts & tweets...")
        content_data = self.content_agent.generate_campaign_content(
            product_name=product_name, target_audience=target_audience, market_insights=market_insights
        )

        # Step 3: SEO Agent
        logger.info("Agent 3/5 [SEO Agent]: Performing SERP keyword mapping, meta tags & SEO scoring...")
        seo_data = self.seo_agent.optimize_campaign_seo(
            product_name=product_name, target_audience=target_audience, content_data=content_data
        )

        # Step 4: Ad Agent
        logger.info("Agent 4/5 [Ad Agent]: Generating Google Search/Display ad copies & budget strategy...")
        ad_data = self.ad_agent.generate_ad_campaign(
            product_name=product_name, target_audience=target_audience, budget=budget
        )

        # Step 5: Analytics Agent
        logger.info("Agent 5/5 [Analytics Agent]: Pulling GA4 benchmarks, modeling ROI & next campaign...")
        analytics_data = self.analytics_agent.analyze_and_project_roi(
            product_name=product_name, target_audience=target_audience, budget=budget, ad_data=ad_data
        )

        # Consolidated Master Campaign Deliverable
        master_campaign = {
            "campaign_id": f"campaign_{product_name.lower().replace(' ', '_')}_1000",
            "product_name": product_name,
            "target_audience": target_audience,
            "budget": budget,
            "market_research": market_insights,
            "content": content_data,
            "seo": seo_data,
            "ad_campaign": ad_data,
            "analytics_and_roi": analytics_data,
        }

        # Save deliverables to /outputs
        self._save_campaign_artifacts(master_campaign)

        logger.info(f"✨ AUTO-GROWTH Campaign Complete! All assets exported to '{self.output_dir}'")
        return master_campaign

    def _save_campaign_artifacts(self, campaign: Dict[str, Any]) -> None:
        """Saves campaign JSON report, markdown blogs, LinkedIn posts, and ad copies to disk."""
        # 1. Save master campaign JSON
        summary_path = os.path.join(self.output_dir, "campaign_summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(campaign, f, indent=2)

        # 2. Save 5 Blogs in /outputs/blogs
        blogs_dir = os.path.join(self.output_dir, "blogs")
        os.makedirs(blogs_dir, exist_ok=True)
        for idx, blog in enumerate(campaign["content"]["blogs"], 1):
            blog_file = os.path.join(blogs_dir, f"blog_{idx}_{blog['slug']}.md")
            seo_info = campaign["seo"]["blog_seo_reports"][idx - 1] if idx <= len(campaign["seo"]["blog_seo_reports"]) else {}
            meta_header = (
                f"<!---\n"
                f"Title: {blog['title']}\n"
                f"Slug: {blog['slug']}\n"
                f"Target Keyword: {blog['target_keyword']}\n"
                f"SEO Score: {seo_info.get('score_breakdown', {}).get('overall_score', 'N/A')}/100\n"
                f"Meta Description: {blog['meta_description']}\n"
                f"--->\n\n"
            )
            with open(blog_file, "w", encoding="utf-8") as f:
                f.write(meta_header + blog["body"])

        # 3. Save 10 LinkedIn Posts
        linkedin_file = os.path.join(self.output_dir, "linkedin_posts.md")
        with open(linkedin_file, "w", encoding="utf-8") as f:
            f.write(f"# 10 Social Media Posts for {campaign['product_name']}\n\n")
            for post in campaign["content"]["linkedin_posts"]:
                f.write(f"--- \n### {post['day']} - {post['theme']} ({post['id']})\n\n{post['content']}\n\n")

        # 4. Save Ad Copies & Budget Allocation Report
        ads_file = os.path.join(self.output_dir, "ad_campaign_strategy.md")
        with open(ads_file, "w", encoding="utf-8") as f:
            f.write(f"# Google Ad Copies & Budget Strategy for {campaign['product_name']}\n\n")
            f.write(f"## Total Budget: ${campaign['budget']:,.2f}\n\n")
            f.write("### Channel Budget Allocation:\n")
            for ch in campaign["ad_campaign"]["budget_allocation"]["channel_breakdown"]:
                f.write(f"- **{ch['channel']}**: ${ch['allocated_amount']:,.2f} ({ch['share_percentage']}) | Est. Clicks: {ch['est_clicks']} @ ${ch['est_cpc']} CPC\n")
            f.write("\n### Google Search Ad Copies:\n")
            for ad in campaign["ad_campaign"]["ad_copies"]["search_ads"]:
                f.write(f"\n#### Variant: {ad['variant_name']}\n")
                f.write("**Headlines:**\n" + "\n".join([f"- {h}" for h in ad["headlines"]]) + "\n")
                f.write("**Descriptions:**\n" + "\n".join([f"- {d}" for d in ad["descriptions"]]) + "\n")

        # 5. Save Executive ROI & Strategy Report
        roi_file = os.path.join(self.output_dir, "roi_and_growth_strategy.md")
        fin = campaign["analytics_and_roi"]["financial_summary"]
        with open(roi_file, "w", encoding="utf-8") as f:
            f.write(f"# Executive ROI & Growth Strategy Report - {campaign['product_name']}\n\n")
            f.write(f"{campaign['analytics_and_roi']['executive_summary']}\n\n")
            f.write("## Financial Projections:\n")
            f.write(f"- **Total Campaign Budget**: ${fin['total_investment']:,.2f}\n")
            f.write(f"- **Estimated Clicks**: {fin['estimated_clicks']}\n")
            f.write(f"- **Expected Leads**: {fin['expected_leads']} (Cost per Lead: ${fin['cost_per_lead']:.2f})\n")
            f.write(f"- **Expected Paid Customers**: {fin['expected_paying_customers']} (CAC: ${fin['customer_acquisition_cost']:.2f})\n")
            f.write(f"- **Projected Revenue**: ${fin['projected_gross_revenue']:,.2f}\n")
            f.write(f"- **Projected Net Profit**: ${fin['projected_net_profit']:,.2f}\n")
            f.write(f"- **Projected ROI**: {fin['roi_percentage']}% ({fin['roi_multiplier']}x ROI)\n\n")
            f.write("## Next Campaign Recommendations:\n")
            for rec in campaign["analytics_and_roi"]["next_campaign_recommendations"]:
                f.write(f"- [{rec['priority']}] **{rec['recommendation']}**: {rec['rationale']}\n")
