import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(page_title="Analytics Dashboard | PASHA-UNIFIED-OS", page_icon="📊", layout="wide")

st.title("📊 Layer 4: Growth & Virality Analytics Dashboard")
st.markdown("Track post views over time, compare predicted vs actual virality scores, monitor follower growth, and analyze top-performing hooks.")

API_URL = os.getenv("API_URL", "http://localhost:8000")

try:
    res = requests.get(f"{API_URL}/analytics", timeout=10)
    data = res.json().get("analytics", []) if res.status_code == 200 else []
except Exception as e:
    data = []
    st.error(f"Could not load analytics from API: {e}")

if not data:
    st.warning("No analytics records found yet. Trigger post publishing and analytics scraping pass.")
    # Show synthetic chart preview
    data = [
        {"post_id": 1, "topic": "Voice AI Latency", "virality_score": 88, "views": 7400, "likes": 520, "comments": 140, "follower_delta": 62, "dm_leads": 15, "scraped_at": "2025-02-20"},
        {"post_id": 2, "topic": "RAG Hybrid Retrieval", "virality_score": 92, "views": 10200, "likes": 810, "comments": 210, "follower_delta": 95, "dm_leads": 24, "scraped_at": "2025-02-21"},
        {"post_id": 3, "topic": "LangGraph Multi-Agent", "virality_score": 85, "views": 6100, "likes": 430, "comments": 110, "follower_delta": 48, "dm_leads": 11, "scraped_at": "2025-02-22"},
        {"post_id": 4, "topic": "DALL-E 3 Visual Carousels", "virality_score": 79, "views": 4800, "likes": 310, "comments": 85, "follower_delta": 32, "dm_leads": 8, "scraped_at": "2025-02-23"},
        {"post_id": 5, "topic": "Sub-300ms Agent Loops", "virality_score": 95, "views": 12800, "likes": 980, "comments": 310, "follower_delta": 140, "dm_leads": 38, "scraped_at": "2025-02-24"}
    ]

df = pd.DataFrame(data)

st.subheader("1. Key Growth Performance Metrics")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Impressions / Views", f"{df['views'].sum():,}")
m2.metric("Total Engagement (Likes + Comments)", f"{df['likes'].sum() + df['comments'].sum():,}")
m3.metric("Follower Growth Delta", f"+{df['follower_delta'].sum()}")
m4.metric("Qualified Inbound DM Leads", f"{df['dm_leads'].sum()} leads")

st.markdown("---")

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📈 Views Over Time")
    fig_views = px.line(
        df,
        x="scraped_at",
        y="views",
        color="topic",
        markers=True,
        title="Post Views & Impressions Trajectory"
    )
    st.plotly_chart(fig_views, use_container_width=True)

with col_right:
    st.subheader("🎯 Virality Scorer Accuracy (Predicted vs Actual Views)")
    fig_corr = px.scatter(
        df,
        x="virality_score",
        y="views",
        size="likes",
        color="topic",
        hover_data=["post_id", "follower_delta"],
        trendline="ols",
        title="Virality Score (0-100) vs Actual LinkedIn Views"
    )
    st.plotly_chart(fig_corr, use_container_width=True)

st.markdown("---")

col_left2, col_right2 = st.columns(2)

with col_left2:
    st.subheader("👥 Follower Delta & Inbound DM Leads")
    fig_leads = px.bar(
        df,
        x="topic",
        y=["follower_delta", "dm_leads"],
        barmode="group",
        title="Followers & DM Lead Generation by Topic"
    )
    st.plotly_chart(fig_leads, use_container_width=True)

with col_right2:
    st.subheader("🏆 Top Performing Hooks & Topics")
    st.dataframe(df[["topic", "virality_score", "views", "likes", "comments", "dm_leads"]].sort_values(by="views", ascending=False))
