import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="Content Calendar | PASHA-UNIFIED-OS", page_icon="📅", layout="wide")

st.title("📅 Layer 2 & 3: Content Calendar & Approval Board")
st.markdown("Notion-style 30-day view of scheduled, pending, and published LinkedIn posts.")

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.sidebar.header("⚡ Action Center")
if st.sidebar.button("🤖 Trigger LangGraph Generation Engine"):
    with st.spinner("Running 4-Node LangGraph (Researcher -> Ghostwriter -> Designer -> Critic)..."):
        try:
            res = requests.post(f"{API_URL}/generate", json={}, timeout=30)
            if res.status_code == 200:
                data = res.json()
                st.sidebar.success(f"Generated Post #{data['post_id']}! Virality Score: {data['post'].get('virality_score')}/100")
                st.rerun()
            else:
                st.sidebar.error(f"Generation failed: {res.text}")
        except Exception as e:
            st.sidebar.error(f"Error connecting to API: {e}")

try:
    res = requests.get(f"{API_URL}/posts/calendar", timeout=10)
    posts = res.json().get("posts", []) if res.status_code == 200 else []
except Exception as e:
    posts = []
    st.error(f"Could not load posts from API: {e}")

tab1, tab2, tab3 = st.tabs(["📌 Pending Approvals Queue", "🗓️ Scheduled Calendar", "📜 Published Posts"])

with tab1:
    pending_posts = [p for p in posts if p.get("status") == "pending_approval"]
    if not pending_posts:
        st.info("No posts pending approval right now! Click 'Trigger LangGraph Generation Engine' in the sidebar.")
    else:
        for p in pending_posts:
            with st.expander(f"🔥 Post #{p['id']} - Topic: {p['topic']} | Virality Score: {p.get('virality_score')}/100", expanded=True):
                col_left, col_right = st.columns([2, 1])
                with col_left:
                    st.markdown(f"**Angle:** `{p['angle']}` | **Predicted Views:** `{p.get('predicted_views')}`")
                    st.code(p['full_text'], language="text")
                with col_right:
                    if p.get("image_url"):
                        st.markdown("**Generated DALL-E 3 Visual:**")
                        st.image(p['image_url'], use_column_width=True)
                    else:
                        st.info("No visual image attached.")

                bcol1, bcol2, bcol3, bcol4 = st.columns(4)
                if bcol1.button(f"✅ Approve & Schedule (9:30 AM)", key=f"app_{p['id']}"):
                    requests.post(f"{API_URL}/approve", json={"post_id": p['id']})
                    st.success("Approved!")
                    st.rerun()
                if bcol2.button(f"❌ Reject", key=f"rej_{p['id']}"):
                    requests.post(f"{API_URL}/reject", json={"post_id": p['id']})
                    st.warning("Rejected.")
                    st.rerun()
                if bcol3.button(f"✏️ Rewrite Hook", key=f"rew_{p['id']}"):
                    requests.post(f"{API_URL}/rewrite-hook", json={"post_id": p['id']})
                    st.info("Hook rewritten!")
                    st.rerun()
                if bcol4.button(f"🔄 Regenerate Image", key=f"reimg_{p['id']}"):
                    requests.post(f"{API_URL}/regenerate-image", json={"post_id": p['id']})
                    st.info("Image regenerated!")
                    st.rerun()

with tab2:
    scheduled_posts = [p for p in posts if p.get("status") == "scheduled"]
    if not scheduled_posts:
        st.info("No scheduled posts currently in queue.")
    else:
        for p in scheduled_posts:
            st.markdown(f"🗓️ **Scheduled for {p.get('scheduled_time', 'Tomorrow 9:30 AM IST')}** | Post #{p['id']}")
            st.text_area("Content", value=p['full_text'], height=120, key=f"sched_{p['id']}")
            if st.button("🚀 Publish Now", key=f"pub_now_{p['id']}"):
                requests.post(f"{API_URL}/publish/now")
                st.success("Published to LinkedIn!")
                st.rerun()
            st.markdown("---")

with tab3:
    published_posts = [p for p in posts if p.get("status") == "published"]
    if not published_posts:
        st.info("No published posts yet.")
    else:
        st.dataframe(pd.DataFrame(published_posts)[["id", "topic", "virality_score", "scheduled_time", "linkedin_post_id"]])
