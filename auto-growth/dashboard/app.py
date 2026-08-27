"""
Streamlit Executive Dashboard for AUTO-GROWTH Autonomous AI Marketing Agency.
Provides interactive campaign control, interactive content calendar, copy library,
Google Ads preview & budget allocation charts, SEO score diagnostics, and GA4 ROI modeling.
"""

import os
import sys
import json
import datetime
import pandas as pd
import streamlit as st
import plotly.express as px

# Path setup
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

try:
    from workflow import AutonomousMarketingWorkflow
except ImportError:
    from auto_growth.workflow import AutonomousMarketingWorkflow

st.set_page_config(
    page_title="AUTO-GROWTH | Autonomous AI Marketing Agency",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS Styling
st.markdown(
    """
    <style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
    }
    .agent-tag {
        background-color: #EEF2FF;
        color: #4338CA;
        font-weight: 600;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.85rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-header">🤖 AUTO-GROWTH — Autonomous AI Marketing Agency</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub-header">Replace your $150k marketing department with 5 CrewAI/LangGraph specialized agents running 24/7.</div>',
    unsafe_allow_html=True,
)

# Sidebar Configuration
st.sidebar.header("🎯 Launch Campaign Engine")
product_input = st.sidebar.text_input("Product / Platform Name", value="PASHA-OS")
target_input = st.sidebar.text_input("Target Audience", value="US startups")
budget_input = st.sidebar.number_input("Campaign Budget ($ USD)", min_value=100.0, max_value=100000.0, value=1000.0, step=100.0)

with st.sidebar.expander("🔑 Optional API Keys"):
    tavily_key = st.text_input("Tavily API Key", type="password")
    perplexity_key = st.text_input("Perplexity API Key", type="password")
    openai_key = st.text_input("OpenAI API Key", type="password")
    serp_key = st.text_input("SERP API Key", type="password")

output_dir = os.path.join(base_dir, "outputs")
summary_path = os.path.join(output_dir, "campaign_summary.json")


def load_campaign_data():
    if os.path.exists(summary_path):
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Run default if none exists
    wf = AutonomousMarketingWorkflow(output_dir=output_dir)
    return wf.run_campaign(product_name=product_input, target_audience=target_input, budget=budget_input)


if st.sidebar.button("🚀 Execute Autonomous Run", type="primary"):
    with st.spinner("🤖 5 AI Agents executing market research, content creation, SEO optimization & ROI modeling..."):
        wf = AutonomousMarketingWorkflow(
            tavily_api_key=tavily_key,
            perplexity_api_key=perplexity_key,
            openai_api_key=openai_key,
            serp_api_key=serp_key,
            output_dir=output_dir,
        )
        campaign_data = wf.run_campaign(product_name=product_input, target_audience=target_input, budget=budget_input)
        st.sidebar.success("✅ Autonomous Campaign Successfully Generated!")
else:
    campaign_data = load_campaign_data()

# Top Summary KPI Metrics
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
fin = campaign_data.get("analytics_and_roi", {}).get("financial_summary", {})

kpi1.metric("Target Product", campaign_data.get("product_name", "N/A"))
kpi2.metric("Campaign Budget", f"${campaign_data.get('budget', 1000):,.0f}")
kpi3.metric("Projected Revenue", f"${fin.get('projected_gross_revenue', 0):,.2f}", f"+{fin.get('roi_percentage', 0)}% ROI")
kpi4.metric("Avg SEO Score", f"{campaign_data.get('seo', {}).get('campaign_avg_seo_score', 0)}/100")
kpi5.metric("Total Assets Generated", f"{campaign_data.get('content', {}).get('blog_count', 5)} Blogs + {campaign_data.get('content', {}).get('linkedin_count', 10)} Social")

st.divider()

# Interactive Tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(
    [
        "📊 Executive Strategy",
        "📅 Content Calendar",
        "📝 Content Library",
        "📢 Google Ads & Budget",
        "🔍 SEO Diagnostics",
        "📈 ROI & Analytics",
    ]
)

# Tab 1: Executive Strategy & Market Research
with tab1:
    st.subheader("🔍 Market Research Agent Insights")
    mr = campaign_data.get("market_research", {})
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown(f"**Industry Overview:** {mr.get('industry_overview', '')}")
        st.markdown(f"**Recommended Positioning:** `{mr.get('recommended_positioning', '')}`")
        st.markdown("#### Top Competitor Matrix")
        competitors = mr.get("top_competitors", [])
        if competitors:
            comp_df = pd.DataFrame(competitors)
            st.dataframe(comp_df, use_container_width=True)

    with col_b:
        st.markdown("#### Target Buyer Personas")
        personas = mr.get("target_buyer_personas", [])
        for p in personas:
            with st.container():
                st.markdown(f"**Role**: `{p.get('role')}`")
                st.markdown(f"*Value Prop*: {p.get('value_proposition')}")
                st.caption("Pain Points: " + ", ".join(p.get("pain_points", [])))
                st.divider()

# Tab 2: Interactive Content Calendar
with tab2:
    st.subheader("📅 Automated 30-Day Campaign Content Calendar")
    st.info("Visual scheduling view for the 5 SEO Blogs and 10 LinkedIn Posts generated autonomously.")

    start_date = datetime.date.today()
    calendar_events = []

    # Map Blogs
    blogs = campaign_data.get("content", {}).get("blogs", [])
    for idx, b in enumerate(blogs):
        event_date = start_date + datetime.timedelta(days=idx * 6)
        calendar_events.append(
            {
                "Date": event_date.strftime("%Y-%m-%d"),
                "Channel": "SEO Blog",
                "Asset Title": b.get("title"),
                "Target Keyword": b.get("target_keyword"),
                "Status": "Scheduled",
            }
        )

    # Map LinkedIn Posts
    posts = campaign_data.get("content", {}).get("linkedin_posts", [])
    for idx, p in enumerate(posts):
        event_date = start_date + datetime.timedelta(days=idx * 3 + 1)
        calendar_events.append(
            {
                "Date": event_date.strftime("%Y-%m-%d"),
                "Channel": "LinkedIn Post",
                "Asset Title": f"{p.get('theme')} ({p.get('id')})",
                "Target Keyword": "Social Thought Leadership",
                "Status": "Scheduled",
            }
        )

    cal_df = pd.DataFrame(calendar_events).sort_values("Date")
    st.dataframe(cal_df, use_container_width=True, height=400)

# Tab 3: Content Library
with tab3:
    st.subheader("📝 Autonomous Asset Library")
    c_sub1, c_sub2 = st.tabs(["📚 5 SEO Blogs", "💼 10 LinkedIn Posts"])

    with c_sub1:
        for idx, b in enumerate(blogs, 1):
            with st.expander(f"Blog #{idx}: {b.get('title')} (Keyword: {b.get('target_keyword')})"):
                st.caption(f"Slug: /blog/{b.get('slug')}")
                st.markdown(b.get("body"))

    with c_sub2:
        for p in posts:
            with st.expander(f"{p.get('day')} - {p.get('theme')}"):
                st.text_area("Post Copy", value=p.get("content"), height=180, key=f"post_{p.get('id')}")

# Tab 4: Google Ads & Budget Allocation
with tab4:
    st.subheader("📢 Ad Agent - Copies & Channel Budget Allocation")
    ad_data = campaign_data.get("ad_campaign", {})
    budget_strat = ad_data.get("budget_allocation", {})

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### Channel Budget Allocation")
        channels = budget_strat.get("channel_breakdown", [])
        if channels:
            ch_df = pd.DataFrame(channels)
            fig = px.pie(
                ch_df,
                names="channel",
                values="allocated_amount",
                title=f"Total Budget Breakdown (${campaign_data.get('budget', 1000):,.0f})",
                color_discrete_sequence=px.colors.sequential.Indigo,
            )
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Estimated Channel Performance")
        if channels:
            fig_bar = px.bar(
                ch_df,
                x="channel",
                y="est_clicks",
                text="est_clicks",
                color="channel",
                title="Estimated Clicks by Channel",
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("#### Google Search Ad Creative Variants")
    search_ads = ad_data.get("ad_copies", {}).get("search_ads", [])
    for ad in search_ads:
        with st.expander(f"Search Ad Variant: {ad.get('variant_name')}"):
            st.write("**Headlines:**", ad.get("headlines"))
            st.write("**Descriptions:**", ad.get("descriptions"))
            st.write("**Keywords:**", ad.get("keywords"))

# Tab 5: SEO Diagnostics
with tab5:
    st.subheader("🔍 SEO Agent Optimization Diagnostics")
    seo_info = campaign_data.get("seo", {})

    st.markdown(f"**Overall Campaign Readiness**: `{seo_info.get('seo_readiness', 'EXCELLENT')}`")
    st.markdown(f"**Average SEO Score**: `{seo_info.get('campaign_avg_seo_score')}/100`")

    reports = seo_info.get("blog_seo_reports", [])
    seo_rows = []
    for r in reports:
        breakdown = r.get("score_breakdown", {})
        seo_rows.append(
            {
                "Blog Title": r.get("title"),
                "Target Keyword": r.get("target_keyword"),
                "Overall Score": breakdown.get("overall_score"),
                "Word Count": breakdown.get("word_count"),
                "Keyword Density %": breakdown.get("keyword_density_pct"),
            }
        )
    st.dataframe(pd.DataFrame(seo_rows), use_container_width=True)

# Tab 6: ROI & Analytics
with tab6:
    st.subheader("📈 Analytics Agent - GA4 ROI Projections")
    analytics = campaign_data.get("analytics_and_roi", {})
    summary_text = analytics.get("executive_summary", "")
    st.success(summary_text)

    fin = analytics.get("financial_summary", {})
    f1, f2, f3, f4 = st.columns(4)
    f1.metric("Cost per Lead (CPL)", f"${fin.get('cost_per_lead', 0):,.2f}")
    f2.metric("Customer Acq Cost (CAC)", f"${fin.get('customer_acquisition_cost', 0):,.2f}")
    f3.metric("Projected Paying Customers", f"{fin.get('expected_paying_customers', 0)}")
    f4.metric("ROI Multiplier", f"{fin.get('roi_multiplier', 0)}x")

    st.divider()
    st.markdown("#### Next Campaign Optimization Recommendations")
    for rec in analytics.get("next_campaign_recommendations", []):
        st.markdown(f"- **[{rec.get('priority')}] {rec.get('recommendation')}**: {rec.get('rationale')}")
