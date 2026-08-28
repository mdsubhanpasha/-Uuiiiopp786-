import streamlit as st
import requests
import os

st.set_page_config(page_title="Queue & Settings | PASHA-UNIFIED-OS", page_icon="⚙️", layout="wide")

st.title("⚙️ Layer 3 & 4: Queue Management & API Configuration")
st.markdown("Configure API credentials, Telegram Bot tokens, posting schedule, and manual execution triggers.")

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.subheader("1. System API Keys & Configuration")

with st.form("settings_form"):
    openai_key = st.text_input("OPENAI_API_KEY", value=os.getenv("OPENAI_API_KEY", ""), type="password")
    tavily_key = st.text_input("TAVILY_API_KEY", value=os.getenv("TAVILY_API_KEY", ""), type="password")
    telegram_token = st.text_input("TELEGRAM_BOT_TOKEN", value=os.getenv("TELEGRAM_BOT_TOKEN", ""), type="password")
    telegram_chat = st.text_input("TELEGRAM_CHAT_ID", value=os.getenv("TELEGRAM_CHAT_ID", ""))
    groq_key = st.text_input("GROQ_API_KEY", value=os.getenv("GROQ_API_KEY", ""), type="password")
    linkedin_token = st.text_input("LINKEDIN_ACCESS_TOKEN", value=os.getenv("LINKEDIN_ACCESS_TOKEN", ""), type="password")

    submit = st.form_submit_button("💾 Save System Settings")

    if submit:
        settings_payload = {
            "OPENAI_API_KEY": openai_key,
            "TAVILY_API_KEY": tavily_key,
            "TELEGRAM_BOT_TOKEN": telegram_token,
            "TELEGRAM_CHAT_ID": telegram_chat,
            "GROQ_API_KEY": groq_key,
            "LINKEDIN_ACCESS_TOKEN": linkedin_token
        }
        try:
            res = requests.post(f"{API_URL}/settings", json={"settings": settings_payload}, timeout=10)
            if res.status_code == 200:
                st.success("✅ Settings updated successfully!")
            else:
                st.error(f"Failed to update settings: {res.text}")
        except Exception as e:
            st.error(f"Error connecting to API: {e}")

st.markdown("---")
st.subheader("2. Manual Execution Triggers")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📰 Fetch Latest AI News")
    if st.button("Fetch News Now"):
        with st.spinner("Fetching trending AI news..."):
            try:
                res = requests.get(f"{API_URL}/news/fetch")
                st.success(f"Fetched {res.json().get('count')} trending AI articles!")
            except Exception as e:
                st.error(f"Error: {e}")

with col2:
    st.markdown("### 💬 Run Auto-Engagement Engine")
    if st.button("Trigger Comment Cycle"):
        with st.spinner("Generating 2-line Groq comments on LinkedIn target posts..."):
            try:
                res = requests.post(f"{API_URL}/engagement/cycle")
                st.success(f"Posted {len(res.json().get('posted_comments', []))} automated technical comments!")
            except Exception as e:
                st.error(f"Error: {e}")

with col3:
    st.markdown("### 🚀 Trigger Immediate Publish")
    if st.button("Publish Queue Now"):
        with st.spinner("Publishing scheduled posts via LinkedIn API..."):
            try:
                res = requests.post(f"{API_URL}/publish/now")
                st.success(f"Publish status: {res.json().get('published')}")
            except Exception as e:
                st.error(f"Error: {e}")
