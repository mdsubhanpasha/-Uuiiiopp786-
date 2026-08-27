#!/usr/bin/env python3
"""
CLI Runner for AUTO-GROWTH Autonomous AI Marketing Agency.
Runs the complete multi-agent campaign pipeline for a given product, target audience, and budget.
"""

import sys
import os
import argparse

# Ensure auto-growth directory is on python path
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from workflow import AutonomousMarketingWorkflow
except ImportError:
    from auto_growth.workflow import AutonomousMarketingWorkflow


def main():
    parser = argparse.ArgumentParser(description="AUTO-GROWTH: Autonomous AI Marketing Agency")
    parser.add_argument("--product", type=str, default="PASHA-OS", help="Name of product/service")
    parser.add_argument("--target", type=str, default="US startups", help="Target buyer persona / audience")
    parser.add_argument("--budget", type=float, default=1000.0, help="Total campaign budget in USD")
    parser.add_argument("--output", type=str, default=None, help="Custom output directory path")

    args = parser.parse_args()

    print("=" * 70)
    print("🤖 AUTO-GROWTH: Autonomous AI Marketing Agency Engine")
    print("=" * 70)
    print(f"Product Input    : {args.product}")
    print(f"Target Audience  : {args.target}")
    print(f"Campaign Budget  : ${args.budget:,.2f}")
    print("=" * 70)

    workflow = AutonomousMarketingWorkflow(output_dir=args.output)
    results = workflow.run_campaign(product_name=args.product, target_audience=args.target, budget=args.budget)

    print("\n" + "=" * 70)
    print("🎉 CAMPAIGN EXECUTION COMPLETE!")
    print("=" * 70)
    print(f"SEO Blogs Generated       : {results['content']['blog_count']}")
    print(f"LinkedIn Posts Generated   : {results['content']['linkedin_count']}")
    print(f"Average SEO Score          : {results['seo']['campaign_avg_seo_score']}/100")
    print(f"Projected Gross Revenue    : ${results['analytics_and_roi']['financial_summary']['projected_gross_revenue']:,.2f}")
    print(f"Projected Net ROI          : {results['analytics_and_roi']['financial_summary']['roi_percentage']}%")
    print("=" * 70)


if __name__ == "__main__":
    main()
