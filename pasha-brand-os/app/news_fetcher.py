import os
import requests
from typing import List, Dict, Any
from datetime import datetime, timezone
from loguru import logger
from app.database import save_news_articles

class NewsFetcher:
    """Fetches trending AI news using Tavily API and NewsAPI.org."""

    def __init__(self, tavily_key: str = None, newsapi_key: str = None):
        self.tavily_key = tavily_key or os.getenv("TAVILY_API_KEY", "")
        self.newsapi_key = newsapi_key or os.getenv("NEWSAPI_KEY", "")
        self.keywords = ["AI", "Voice AI", "RAG", "Multi-Agent Systems", "LLMs", "LangGraph", "CrewAI"]

    def fetch_tavily_news(self) -> List[Dict[str, Any]]:
        if not self.tavily_key or self.tavily_key.startswith("tvly-placeholder"):
            logger.info("Tavily key not set or placeholder. Returning synthetic AI news.")
            return self._generate_synthetic_news("Tavily")

        articles = []
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=self.tavily_key)
            response = client.search(
                query="Latest trends breakthroughs in AI Voice AI RAG Multi-Agent LLM",
                search_depth="advanced",
                max_results=10
            )
            for item in response.get("results", []):
                articles.append({
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),
                    "source_url": item.get("url", ""),
                    "category": "AI/RAG",
                    "relevance_score": round(float(item.get("score", 0.85)) * 100, 2),
                    "published_at": datetime.now(timezone.utc).isoformat()
                })
        except Exception as e:
            logger.error(f"Error fetching Tavily news: {e}")
            articles = self._generate_synthetic_news("Tavily-Fallback")
        return articles

    def fetch_newsapi_news(self) -> List[Dict[str, Any]]:
        if not self.newsapi_key or self.newsapi_key.startswith("placeholder"):
            logger.info("NewsAPI key not set. Returning synthetic AI news.")
            return self._generate_synthetic_news("NewsAPI")

        articles = []
        try:
            url = f"https://newsapi.org/v2/everything?q=Artificial+Intelligence+OR+Voice+AI+OR+RAG&sortBy=publishedAt&pageSize=10&apiKey={self.newsapi_key}"
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                data = res.json()
                for item in data.get("articles", []):
                    articles.append({
                        "title": item.get("title", ""),
                        "content": item.get("description", "") or item.get("content", ""),
                        "source_url": item.get("url", ""),
                        "category": "AI News",
                        "relevance_score": 88.5,
                        "published_at": item.get("publishedAt", datetime.now(timezone.utc).isoformat())
                    })
        except Exception as e:
            logger.error(f"Error fetching NewsAPI news: {e}")
            articles = self._generate_synthetic_news("NewsAPI-Fallback")
        return articles

    def _generate_synthetic_news(self, source_name: str) -> List[Dict[str, Any]]:
        return [
            {
                "title": "Autonomous Multi-Agent Systems Revolutionize Enterprise Software Engineering",
                "content": "New benchmarks show 10x developer velocity when deploying specialized LangGraph and CrewAI multi-agent swarms with strict human-in-the-loop validation.",
                "source_url": f"https://techcrunch.com/synthetic/{source_name.lower()}-multi-agent-breakthrough",
                "category": "Multi-Agent",
                "relevance_score": 96.5,
                "published_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "title": "Sub-300ms Voice AI Agents Transform Real-Time Customer Support",
                "content": "Deepgram Nova-2 and ElevenLabs streaming pipelines combined with LLMs now handle over 50k calls concurrently with human-level cadence.",
                "source_url": f"https://venturebeat.com/synthetic/{source_name.lower()}-voice-ai-latency",
                "category": "Voice AI",
                "relevance_score": 94.0,
                "published_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "title": "Self-Correcting RAG Architectures Eliminate Hallucinations in Financial AI",
                "content": "Hybrid BM25 dense retrieval paired with Cross-Encoder reranking and NLI guardrails achieve 99.4% accuracy in factual evaluation tasks.",
                "source_url": f"https://arxiv.org/synthetic/{source_name.lower()}-self-correcting-rag",
                "category": "RAG",
                "relevance_score": 92.0,
                "published_at": datetime.now(timezone.utc).isoformat()
            }
        ]

    def fetch_all_trending_news(self, db_path: str = None) -> List[Dict[str, Any]]:
        logger.info("Fetching trending AI news from Tavily and NewsAPI...")
        tavily_articles = self.fetch_tavily_news()
        newsapi_articles = self.fetch_newsapi_news()

        combined = tavily_articles + newsapi_articles
        # Deduplicate by URL
        unique_articles = {}
        for art in combined:
            url = art.get("source_url")
            if url and url not in unique_articles:
                unique_articles[url] = art

        sorted_articles = sorted(list(unique_articles.values()), key=lambda x: x["relevance_score"], reverse=True)[:20]

        if db_path:
            save_news_articles(sorted_articles, db_path=db_path)

        return sorted_articles
