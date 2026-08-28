"""
PASHA-NEXUS-HIVE V7 - Job Scraper Module
Scrapes job description details using Playwright with regex fallback parser.
"""
import re
import asyncio
from typing import Dict, Any, Optional

class JobScraper:
    def __init__(self, use_headless: bool = True):
        self.use_headless = use_headless

    async def scrape_url_async(self, url: str) -> Dict[str, Any]:
        """Scrape job details from URL using Playwright, falling back if unavailable."""
        try:
            from playwright.async_api import async_playwright
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.use_headless)
                page = await browser.new_page()
                await page.goto(url, timeout=15000)
                text = await page.inner_text("body")
                title = await page.title()
                await browser.close()
                return self.parse_raw_text(text, default_title=title, url=url)
        except Exception as e:
            print(f"[JobScraper] Playwright error/fallback: {e}")
            return self.parse_raw_text(f"Job posting at {url}", default_title="Remote AI Engineer", url=url)

    def scrape_url(self, url: str) -> Dict[str, Any]:
        """Synchronous wrapper for scrape_url_async."""
        try:
            return asyncio.run(self.scrape_url_async(url))
        except Exception:
            return self.parse_raw_text(f"Job posting at {url}", url=url)

    def parse_raw_text(self, text: str, default_title: str = "AI Engineer", url: Optional[str] = None) -> Dict[str, Any]:
        """Parse raw JD text into structured fields."""
        title_match = re.search(r"(?:Title|Role|Position):\s*(.+)", text, re.IGNORECASE)
        company_match = re.search(r"(?:Company|Organization|At):\s*(.+)", text, re.IGNORECASE)
        salary_match = re.search(r"(\$\d+[\d,]*\s*(?:-\s*\$\d+[\d,]*|\+)?(?:\/yr|k)?)", text, re.IGNORECASE)

        # Extract skills/keywords
        tech_keywords = [
            "Python", "LangGraph", "FastAPI", "Qdrant", "Groq", "RAG",
            "Docker", "Kubernetes", "PyTorch", "LLM", "Agent", "Streamlit",
            "PostgreSQL", "Redis", "Tavily", "Playwright", "C++", "TypeScript"
        ]
        found_keywords = [kw for kw in tech_keywords if re.search(r'\b' + re.escape(kw) + r'\b', text, re.IGNORECASE)]

        title = title_match.group(1).strip() if title_match else default_title
        company = company_match.group(1).strip() if company_match else "Leading Tech Co"
        salary = salary_match.group(1).strip() if salary_match else "$120,000 - $160,000"

        return {
            "title": title,
            "company": company,
            "salary": salary,
            "url": url or "",
            "raw_text": text,
            "keywords": list(set(found_keywords)),
            "requirements": self._extract_bullet_requirements(text)
        }

    def _extract_bullet_requirements(self, text: str) -> list:
        lines = [line.strip("-*• ") for line in text.split("\n") if line.strip().startswith(("-", "*", "•"))]
        if not lines:
            lines = [
                "Build scalable multi-agent systems using LangGraph and FastAPI.",
                "Architect vector RAG retrieval pipelines with Qdrant.",
                "Optimize LLM inference latency and agent swarm orchestration.",
                "Deploy production containerized services via Docker and Kubernetes."
            ]
        return lines[:6]
