"""
FastAPI Backend Service for AUTO-GROWTH Autonomous AI Marketing Agency.
Exposes REST endpoints to trigger multi-agent campaign workflows, fetch generated outputs, and monitor health.
"""

import os
import sys
import json
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Ensure auto-growth path is available
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from workflow import AutonomousMarketingWorkflow
except ImportError:
    from auto_growth.workflow import AutonomousMarketingWorkflow

app = FastAPI(
    title="AUTO-GROWTH AI Agency API",
    description="REST API for Autonomous AI Marketing Agency running 5 CrewAI agents.",
    version="1.0.0",
)


class CampaignRequest(BaseModel):
    product_name: str = Field(default="PASHA-OS", description="Name of product or enterprise platform")
    target_audience: str = Field(default="US startups", description="Target buyer demographic / market segment")
    budget: float = Field(default=1000.0, description="Campaign marketing budget in USD")
    tavily_api_key: Optional[str] = None
    perplexity_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    serp_api_key: Optional[str] = None


@app.get("/api/v1/campaign/health", tags=["Health"])
def health_check():
    """Service health check endpoint."""
    return {
        "status": "healthy",
        "service": "AUTO-GROWTH Autonomous AI Marketing Agency API",
        "agents": ["Market Research Agent", "Content Agent", "SEO Agent", "Ad Agent", "Analytics Agent"],
    }


@app.post("/api/v1/campaign/run", tags=["Campaign"])
def run_campaign(request: CampaignRequest):
    """Triggers the full 5-agent autonomous campaign workflow synchronously."""
    try:
        workflow = AutonomousMarketingWorkflow(
            tavily_api_key=request.tavily_api_key,
            perplexity_api_key=request.perplexity_api_key,
            openai_api_key=request.openai_api_key,
            serp_api_key=request.serp_api_key,
        )
        results = workflow.run_campaign(
            product_name=request.product_name,
            target_audience=request.target_audience,
            budget=request.budget,
        )
        return {
            "status": "success",
            "message": "Autonomous campaign workflow executed successfully.",
            "data": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Campaign execution failed: {str(e)}")


@app.get("/api/v1/campaign/latest", tags=["Campaign"])
def get_latest_campaign():
    """Retrieves the latest campaign summary generated in /outputs/campaign_summary.json."""
    output_dir = os.path.join(base_dir, "outputs")
    summary_path = os.path.join(output_dir, "campaign_summary.json")

    if not os.path.exists(summary_path):
        # Run default campaign if none exists
        workflow = AutonomousMarketingWorkflow(output_dir=output_dir)
        workflow.run_campaign(product_name="PASHA-OS", target_audience="US startups", budget=1000.0)

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            summary_data = json.load(f)
        return {"status": "success", "data": summary_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read campaign outputs: {str(e)}")
