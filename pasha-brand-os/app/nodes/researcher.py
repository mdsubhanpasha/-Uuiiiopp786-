import os
from typing import Dict, Any, List
from loguru import logger
from app.news_fetcher import NewsFetcher

class ResearcherNode:
    """
    Node 1 - Researcher
    Uses Tavily to pick 1 trending topic, generates 3 unique angles (Contrarian, How-To, Story),
    outputs {topic, angle, source_urls}.
    """
    def __init__(self):
        self.news_fetcher = NewsFetcher()

    def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("Executing Node 1: Researcher...")

        # Override topic if provided in state
        custom_topic = state.get("topic")
        if custom_topic:
            topic = custom_topic
            source_urls = state.get("source_urls", ["https://arxiv.org/abs/2401.00001"])
        else:
            news = self.news_fetcher.fetch_all_trending_news()
            if news:
                top_item = news[0]
                topic = top_item.get("title", "Autonomous Multi-Agent Architecture Trends")
                source_urls = [top_item.get("source_url", "https://arxiv.org/abs/2401.00001")]
            else:
                topic = "Production Multi-Agent Architectures with LangGraph"
                source_urls = ["https://arxiv.org/abs/2401.00001"]

        angles = [
            {
                "type": "Contrarian",
                "title": "Why RAG isn't enough: The rise of stateful Multi-Agent execution",
                "description": "Contrarian take explaining why simple RAG pipelines fail in enterprise production."
            },
            {
                "type": "How-To",
                "title": "How to deploy sub-300ms Voice AI agents using LangGraph & Deepgram",
                "description": "Step-by-step technical guide with concrete benchmark metrics."
            },
            {
                "type": "Story",
                "title": "How we scaled our multi-agent pipeline from 10 to 100k requests/day",
                "description": "Personal engineering story detailing failures, bottlenecks, and breakthroughs."
            }
        ]

        selected_angle = state.get("angle") or angles[0]["type"]

        logger.info(f"Researcher selected topic: '{topic}' with angle '{selected_angle}'")
        return {
            "topic": topic,
            "angle": selected_angle,
            "available_angles": angles,
            "source_urls": source_urls
        }
