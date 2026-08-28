import streamlit as st
import requests
import pandas as pd
import os

st.set_page_config(page_title="Style Cloner | PASHA-UNIFIED-OS", page_icon="🎨", layout="wide")

st.title("🎨 Layer 1: Style Cloner & Vector Ingestion")
st.markdown("Upload a CSV of your past top-performing LinkedIn posts to clone your writing tone, structure, and vocabulary into **Qdrant collection `user_style`**.")

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.subheader("1. Upload LinkedIn Past Posts CSV")
st.caption("Required column: `post_text`. Optional columns: `likes`, `views`.")

uploaded_file = st.file_uploader("Choose a CSV file", type=["csv"])

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.write("### Preview of Uploaded Data:", df.head(5))

        if st.button("🚀 Ingest & Generate Qdrant Embeddings"):
            with st.spinner("Generating embeddings via OpenAI `text-embedding-3-small` and upserting into Qdrant..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")}
                try:
                    res = requests.post(f"{API_URL}/ingest-style", files=files, timeout=30)
                    if res.status_code == 200:
                        data = res.json()
                        st.success(f"✅ Style cloned! {data.get('message')}")
                        st.json(data)
                    else:
                        st.error(f"Failed to ingest: {res.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend API: {e}")
    except Exception as e:
        st.error(f"Invalid CSV file format: {e}")

st.markdown("---")
st.subheader("2. Sample Post CSV Template")
sample_data = pd.DataFrame([
    {
        "post_text": "Most developers build AI agents wrong. They connect LLMs directly to APIs without deterministic state machines.\nHere is how we scaled our LangGraph pipeline to 100k requests/day with sub-300ms latency...\n\nWhat is your team's approach to state memory?",
        "likes": 420,
        "views": 15400
    },
    {
        "post_text": "Sub-300ms Voice AI is no longer a luxury—it's the baseline requirement.\nWe combined Deepgram Nova-2 with Groq Llama-3.3-70b. Response times dropped by 70%.\n\nAre you building real-time voice apps in 2025?",
        "likes": 890,
        "views": 32000
    }
])
st.dataframe(sample_data)

csv_bytes = sample_data.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download Sample CSV Template",
    data=csv_bytes,
    file_name="sample_linkedin_style.csv",
    mime="text/csv"
)
