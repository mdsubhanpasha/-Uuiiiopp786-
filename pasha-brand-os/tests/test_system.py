import os
import pytest
import pandas as pd
from fastapi.testclient import TestClient

from app.database import init_db, insert_post, get_posts, get_post_by_id, update_post_status
from app.qdrant_service import QdrantStyleService
from app.news_fetcher import NewsFetcher
from app.competitor_tracker import CompetitorTracker
from app.graph import BrandOSGraph
from app.auto_engagement import AutoEngagementEngine
from app.publisher import PublisherEngine
from app.main import app

TEST_DB = "app/test_pasha_brand_os.db"

@pytest.fixture(autouse=True)
def setup_test_environment():
    os.environ["DATABASE_PATH"] = TEST_DB
    init_db(TEST_DB)
    yield
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)

def test_database_crud():
    post_data = {
        "topic": "Voice AI Latency",
        "angle": "How-To",
        "variant_type": "Technical deep-dive",
        "hook": "Sub-300ms Voice AI is mandatory.",
        "full_text": "Sub-300ms Voice AI is mandatory in production.",
        "virality_score": 90,
        "status": "pending_approval"
    }
    post_id = insert_post(post_data, db_path=TEST_DB)
    assert post_id > 0

    retrieved = get_post_by_id(post_id, db_path=TEST_DB)
    assert retrieved is not None
    assert retrieved["topic"] == "Voice AI Latency"

    update_post_status(post_id, "scheduled", scheduled_time="2025-02-25T09:30:00Z", db_path=TEST_DB)
    updated = get_post_by_id(post_id, db_path=TEST_DB)
    assert updated["status"] == "scheduled"
    assert updated["scheduled_time"] == "2025-02-25T09:30:00Z"

def test_qdrant_style_cloning():
    qdrant = QdrantStyleService()
    df = pd.DataFrame([
        {"post_text": "Here is how we scaled our multi-agent LangGraph workflow to 100k requests/day.", "likes": 500, "views": 20000},
        {"post_text": "Vector search alone fails on complex technical documentation. Hybrid BM25 is key.", "likes": 300, "views": 12000}
    ])
    res = qdrant.ingest_posts_csv(df)
    assert res["status"] == "success"
    assert res["count"] == 2

    similar = qdrant.search_similar_style("LangGraph scaling", limit=2)
    assert len(similar) > 0

def test_news_and_competitor_fetchers():
    fetcher = NewsFetcher()
    news = fetcher.fetch_all_trending_news(db_path=TEST_DB)
    assert len(news) > 0
    assert "title" in news[0]

    tracker = CompetitorTracker()
    hooks = tracker.scrape_and_analyze_hooks(db_path=TEST_DB)
    assert len(hooks) > 0
    assert "hook_text" in hooks[0]

def test_langgraph_workflow():
    graph = BrandOSGraph()
    state = graph.run(topic="Sub-300ms Voice AI", angle="How-To")
    assert state.get("virality_score") >= 75
    assert "full_text" in state
    assert len(state.get("variants", {})) > 0

def test_auto_engagement_and_publisher():
    eng = AutoEngagementEngine()
    comments = eng.run_engagement_cycle(db_path=TEST_DB)
    assert len(comments) > 0

    pub = PublisherEngine()
    analytics = pub.scrape_analytics_for_published_posts(db_path=TEST_DB)
    assert isinstance(analytics, list)

def test_fastapi_endpoints():
    client = TestClient(app)
    res = client.get("/")
    assert res.status_code == 200
    assert res.json()["system"] == "PASHA-UNIFIED-OS"

    metrics_res = client.get("/metrics")
    assert metrics_res.status_code == 200
