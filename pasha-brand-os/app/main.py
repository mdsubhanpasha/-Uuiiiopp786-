import os
import io
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import pandas as pd
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from loguru import logger
from prometheus_fastapi_instrumentator import Instrumentator

from apscheduler.schedulers.background import BackgroundScheduler

from app.database import (
    init_db, insert_post, get_posts, get_post_by_id, update_post_status,
    update_post_content, get_all_analytics, get_top_news, set_setting, get_setting
)
from app.qdrant_service import QdrantStyleService
from app.news_fetcher import NewsFetcher
from app.competitor_tracker import CompetitorTracker
from app.graph import BrandOSGraph
from app.publisher import PublisherEngine
from app.auto_engagement import AutoEngagementEngine
from bot.telegram_bot import TelegramApprovalBot

app = FastAPI(
    title="PASHA-UNIFIED-OS API",
    description="Autonomous LinkedIn Personal Branding OS - Production Backend API",
    version="1.0.0"
)

# Prometheus Instrumentation Endpoint (/metrics)
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Global engine instances
qdrant_service = QdrantStyleService()
news_fetcher = NewsFetcher()
competitor_tracker = CompetitorTracker()
graph_engine = BrandOSGraph()
publisher_engine = PublisherEngine()
engagement_engine = AutoEngagementEngine()
telegram_bot = TelegramApprovalBot()
scheduler = BackgroundScheduler()

def scheduled_publisher_job():
    logger.info("[APScheduler] Executing periodic queue publishing check...")
    db_path = os.getenv("DATABASE_PATH", "app/pasha_brand_os.db")
    publisher_engine.publish_scheduled_posts(db_path=db_path)

def scheduled_news_job():
    logger.info("[APScheduler] Executing periodic 6-hour news fetch job...")
    db_path = os.getenv("DATABASE_PATH", "app/pasha_brand_os.db")
    news_fetcher.fetch_all_trending_news(db_path=db_path)

def scheduled_engagement_job():
    logger.info("[APScheduler] Executing periodic 2-hour auto-engagement cycle...")
    db_path = os.getenv("DATABASE_PATH", "app/pasha_brand_os.db")
    engagement_engine.run_engagement_cycle(db_path=db_path)

@app.on_event("startup")
def startup_event():
    init_db()

    # Configure and start APScheduler jobs
    scheduler.add_job(scheduled_publisher_job, 'interval', minutes=1, id="publisher_job", replace_existing=True)
    scheduler.add_job(scheduled_news_job, 'interval', hours=6, id="news_job", replace_existing=True)
    scheduler.add_job(scheduled_engagement_job, 'interval', hours=2, id="engagement_job", replace_existing=True)
    scheduler.start()
    logger.info("APScheduler background jobs started (Publisher: 1m, News: 6h, Engagement: 2h).")

    # Start Telegram bot polling thread if app instance configured
    if telegram_bot.app:
        bot_thread = threading.Thread(target=telegram_bot.run_polling, daemon=True)
        bot_thread.start()
        logger.info("Telegram Bot polling thread started in background.")

    logger.info("PASHA-UNIFIED-OS FastAPI started successfully.")

@app.on_event("shutdown")
def shutdown_event():
    if scheduler.running:
        scheduler.shutdown()
        logger.info("APScheduler stopped.")

# Pydantic Request/Response Models
class GeneratePostRequest(BaseModel):
    topic: Optional[str] = None
    angle: Optional[str] = None

class ApprovePostRequest(BaseModel):
    post_id: int
    scheduled_time: Optional[str] = None

class RejectPostRequest(BaseModel):
    post_id: int
    feedback: Optional[str] = "Rejected by user"

class RewriteHookRequest(BaseModel):
    post_id: int
    instructions: Optional[str] = "Make hook punchier"

class SaveSettingsRequest(BaseModel):
    settings: Dict[str, str]

# API Endpoints

@app.get("/")
def read_root():
    return {
        "system": "PASHA-UNIFIED-OS",
        "status": "operational",
        "layers": [
            "Layer 1: Ingestion & Intelligence",
            "Layer 2: LangGraph Generation Engine",
            "Layer 3: Human-in-the-Loop Approval",
            "Layer 4: Publishing & Growth Engine"
        ]
    }

@app.post("/ingest-style")
async def ingest_style(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="File must be a CSV.")

    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))
        res = qdrant_service.ingest_posts_csv(df)
        return {"status": "success", "message": f"Ingested {res['count']} posts into Qdrant collection '{res['collection']}'", "details": res}
    except Exception as e:
        logger.error(f"Error ingesting style CSV: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/news/fetch")
def fetch_news():
    articles = news_fetcher.fetch_all_trending_news(db_path=os.getenv("DATABASE_PATH", "app/pasha_brand_os.db"))
    return {"status": "success", "count": len(articles), "news": articles}

@app.get("/competitors/hooks")
def fetch_competitor_hooks():
    hooks = competitor_tracker.get_top_hooks(limit=10, db_path=os.getenv("DATABASE_PATH", "app/pasha_brand_os.db"))
    return {"status": "success", "count": len(hooks), "hooks": hooks}

@app.post("/generate")
def generate_post(req: GeneratePostRequest):
    try:
        final_state = graph_engine.run(topic=req.topic, angle=req.angle)

        post_data = {
            "topic": final_state.get("topic", ""),
            "angle": final_state.get("angle", ""),
            "variant_type": final_state.get("selected_variant_type", "Story"),
            "hook": final_state.get("hook", ""),
            "problem": final_state.get("problem", ""),
            "insight": final_state.get("insight", ""),
            "cta": final_state.get("cta", ""),
            "full_text": final_state.get("full_text", ""),
            "hashtags": final_state.get("hashtags", ""),
            "image_url": final_state.get("image_url", ""),
            "image_prompt": final_state.get("selected_prompt", ""),
            "virality_score": final_state.get("virality_score", 80),
            "predicted_views": final_state.get("predicted_views", "5k-8k views"),
            "feedback": final_state.get("feedback", ""),
            "status": "pending_approval"
        }

        post_id = insert_post(post_data)
        post_data["id"] = post_id
        post_data["source_urls"] = ", ".join(final_state.get("source_urls", []))

        telegram_bot.send_post_approval_sync(post_data)

        return {"status": "success", "post_id": post_id, "post": post_data}
    except Exception as e:
        logger.error(f"Error in post generation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/posts/pending")
def get_pending_posts():
    posts = get_posts(status="pending_approval")
    return {"status": "success", "count": len(posts), "posts": posts}

@app.get("/posts/calendar")
def get_calendar_posts():
    posts = get_posts()
    return {"status": "success", "count": len(posts), "posts": posts}

@app.post("/approve")
def approve_post(req: ApprovePostRequest):
    post = get_post_by_id(req.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    scheduled_time = req.scheduled_time or datetime.now(timezone.utc).isoformat()
    update_post_status(req.post_id, status="scheduled", scheduled_time=scheduled_time)
    return {"status": "success", "post_id": req.post_id, "post_status": "scheduled", "scheduled_time": scheduled_time}

@app.post("/reject")
def reject_post(req: RejectPostRequest):
    update_post_status(req.post_id, status="rejected")
    update_post_content(req.post_id, feedback=req.feedback)
    return {"status": "success", "post_id": req.post_id, "post_status": "rejected"}

@app.post("/rewrite-hook")
def rewrite_hook(req: RewriteHookRequest):
    post = get_post_by_id(req.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    old_text = post["full_text"]
    lines = old_text.split("\n")
    new_hook = f"🔥 STOP scrolling! Here is why {post['topic']} changes everything in 2025:"
    lines[0] = new_hook
    updated_text = "\n".join(lines)

    update_post_content(req.post_id, full_text=updated_text, hook=new_hook)
    updated_post = get_post_by_id(req.post_id)
    return {"status": "success", "post_id": req.post_id, "post": updated_post}

@app.post("/regenerate-image")
def regenerate_image(req: RewriteHookRequest):
    post = get_post_by_id(req.post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found.")

    res = graph_engine.designer.execute({"topic": post["topic"], "hook": post["hook"]})
    new_url = res.get("image_url", "")
    update_post_content(req.post_id, image_url=new_url)
    updated_post = get_post_by_id(req.post_id)
    return {"status": "success", "post_id": req.post_id, "post": updated_post}

@app.post("/publish/now")
def publish_now():
    res = publisher_engine.publish_scheduled_posts(db_path=os.getenv("DATABASE_PATH", "app/pasha_brand_os.db"))
    return {"status": "success", "published": res}

@app.post("/engagement/cycle")
def run_engagement_cycle():
    comments = engagement_engine.run_engagement_cycle(db_path=os.getenv("DATABASE_PATH", "app/pasha_brand_os.db"))
    return {"status": "success", "posted_comments": comments}

@app.get("/analytics")
def get_analytics():
    publisher_engine.scrape_analytics_for_published_posts(db_path=os.getenv("DATABASE_PATH", "app/pasha_brand_os.db"))
    analytics = get_all_analytics()
    return {"status": "success", "count": len(analytics), "analytics": analytics}

@app.get("/settings")
def get_settings():
    keys = ["OPENAI_API_KEY", "TELEGRAM_BOT_TOKEN", "TELEGRAM_CHAT_ID", "LINKEDIN_ACCESS_TOKEN", "GROQ_API_KEY"]
    res = {k: get_setting(k, default=os.getenv(k, "")) for k in keys}
    return {"status": "success", "settings": res}

@app.post("/settings")
def save_settings(req: SaveSettingsRequest):
    for k, v in req.settings.items():
        set_setting(k, v)
        os.environ[k] = v
    return {"status": "success", "message": "Settings saved successfully."}
