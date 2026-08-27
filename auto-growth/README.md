# 🤖 AUTO-GROWTH — Autonomous AI Marketing Agency

**AUTO-GROWTH** is an enterprise autonomous AI marketing agency that replaces a full marketing department by coordinating 5 specialized agents built with CrewAI and LangGraph patterns.

---

## 🏛️ System Architecture

```
User Input ("Product is PASHA-OS, target US startups, budget $1000")
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│            AutonomousMarketingWorkflow Orchestrator             │
└───────────────────────────────┬─────────────────────────────────┘
                                │
   ┌────────────────────────────┼────────────────────────────┐
   │                            │                            │
   ▼                            ▼                            ▼
┌──────────────────────┐  ┌──────────────────────┐  ┌──────────────────────┐
│ Market Research Agent│  │    Content Agent     │  │      SEO Agent       │
│  (Tavily/Perplexity) │  │  (GPT-4o Engine)     │  │ (SERP API / Scoring) │
└──────────┬───────────┘  └──────────┬───────────┘  └──────────┬───────────┘
           │                         │                         │
           └─────────────────────────┼─────────────────────────┘
                                     │
   ┌─────────────────────────────────┴─────────────────────────┐
   │                                                           │
   ▼                                                           ▼
┌──────────────────────┐                    ┌──────────────────────┐
│       Ad Agent       │                    │   Analytics Agent    │
│(Google Ads & Budget) │                    │  (Mock GA4 DB & ROI) │
└──────────┬───────────┘                    └──────────┬───────────┘
           │                                           │
           └─────────────────────┬─────────────────────┘
                                 │
                                 ▼
                     ┌───────────────────────┐
                     │ /auto-growth/outputs  │
                     │ (JSON, Blogs, Social, │
                     │   Ads, ROI Reports)   │
                     └───────────────────────┘
```

---

## 🤖 The 5 Autonomous Agents

1. **Market Research Agent** (`agents/market_research_agent.py`)
   - Researches competitor positioning, strengths/weaknesses, and buyer personas using live Tavily and Perplexity APIs (with intelligent fallback synthesis).
2. **Content Agent** (`agents/content_agent.py`)
   - Generates 5 long-form markdown SEO blogs, 10 strategic LinkedIn thought leadership posts, and promotional tweets via GPT-4o architecture.
3. **SEO Agent** (`agents/seo_agent.py`)
   - Performs SERP API keyword mapping, meta title & description generation, canonical URL tagging, and calculates deterministic SEO readiness scores.
4. **Ad Agent** (`agents/ad_agent.py`)
   - Creates Google Search & Display ad copies with high-converting headlines and calculates multi-channel budget allocation (Google Search, LinkedIn Ads, Display).
5. **Analytics Agent** (`agents/analytics_agent.py`)
   - Connects to Mock GA4 Analytics DB, models financial CAC, CPL, expected paying customers, projects gross revenue and net ROI for the given budget, and suggests next campaign iterations.

---

## 🚀 Quickstart Guide

### 1. Execute via CLI Runner
To run a full autonomous campaign workflow:
```bash
python3 auto-growth/run_campaign.py --product "PASHA-OS" --target "US startups" --budget 1000
```

### 2. Start FastAPI REST Server
```bash
python3 -m uvicorn auto_growth.api.main:app --port 8000 --reload
# Or navigate to auto-growth and run:
python3 -m uvicorn api.main:app --port 8000
```
- **API Endpoints**:
  - `GET /api/v1/campaign/health` - Health check & active agent list
  - `POST /api/v1/campaign/run` - Trigger autonomous campaign workflow
  - `GET /api/v1/campaign/latest` - Fetch latest generated campaign output

### 3. Launch Streamlit Executive Dashboard
```bash
streamlit run auto-growth/dashboard/app.py
```

---

## 📊 Sample Campaign Output (PASHA-OS)

For input prompt: **"Product is PASHA-OS, target US startups, budget $1000"**

### Executive ROI Summary
- **Total Budget**: $1,000.00
- **Estimated Ad Clicks**: 210 clicks across Search, LinkedIn, and Display
- **Expected Leads**: 9 Enterprise Leads (Cost per Lead: $111.11)
- **Expected Paying Customers**: 2 Enterprise Accounts
- **Customer Acquisition Cost (CAC)**: $500.00
- **Projected Gross Revenue**: **$7,000.00**
- **Projected Net ROI**: **600.0% (7.0x ROI Multiplier)**
- **Average Campaign SEO Score**: **85.0 / 100 (EXCELLENT)**

### Generated Deliverables in `/auto-growth/outputs/`
- `campaign_summary.json` - Complete structured JSON representation of the campaign.
- `blogs/` - 5 high-converting Markdown SEO blogs with meta tags and header markup.
- `linkedin_posts.md` - 10 social media posts scheduled over 30 days.
- `ad_campaign_strategy.md` - Google Ad copies and channel budget allocation breakdown.
- `roi_and_growth_strategy.md` - GA4 ROI modeling and next campaign recommendations.

---

## 🧪 Testing

To run the complete AUTO-GROWTH test suite:
```bash
cd auto-growth
python3 -m pytest tests/ -v
```
