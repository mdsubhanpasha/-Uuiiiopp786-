"""
PASHA-NEURO-RAG Streamlit Interactive UI
Author: Mohammad Subhan Pasha
Perplexity-style enterprise chat UI with citations, groundedness badge, and document drawer.
"""

import streamlit as st
import requests
import json
import time

API_BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="PASHA-NEURO-RAG | Self-Correcting Enterprise RAG",
    page_icon="🧠",
    layout="wide"
)

# Custom CSS for Perplexity style card look
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E293B;
        margin-bottom: 0px;
    }
    .sub-header {
        font-size: 1.0rem;
        color: #64748B;
        margin-bottom: 25px;
    }
    .citation-badge {
        display: inline-block;
        background-color: #E0F2FE;
        color: #0369A1;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.82rem;
        font-weight: 600;
        margin-right: 6px;
        margin-bottom: 6px;
    }
    .grounded-badge-success {
        background-color: #DCFCE7;
        color: #15803D;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .grounded-badge-warning {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/brain.png", width=64)
    st.title("PASHA-NEURO-RAG")
    st.caption("Self-Correcting Enterprise RAG System")
    st.caption("Author: **Mohammad Subhan Pasha**")
    st.markdown("---")

    st.subheader("📄 Document Ingestion")
    upload_file = st.file_uploader("Upload PDF / DOCX Document", type=["pdf", "docx"])
    if upload_file is not None:
        if st.button("Process Document", use_container_width=True):
            with st.spinner("Ingesting and generating semantic chunks..."):
                try:
                    files = {"file": (upload_file.name, upload_file.getvalue())}
                    resp = requests.post(f"{API_BASE_URL}/ingest", files=files)
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Ingested {data['chunk_count']} chunks from {data['source_name']}")
                    else:
                        st.error(f"Failed to ingest document: {resp.text}")
                except Exception as e:
                    st.error(f"Error connecting to backend API: {e}")

    st.markdown("---")
    st.subheader("🌐 Web & Notion Ingestion")
    url_input = st.text_input("Ingest Web URL / Notion Link")
    if url_input:
        if st.button("Ingest URL", use_container_width=True):
            with st.spinner("Fetching and indexing web content..."):
                try:
                    resp = requests.post(f"{API_BASE_URL}/ingest", data={"url": url_input, "source_type": "url"})
                    if resp.status_code == 200:
                        data = resp.json()
                        st.success(f"Indexed {data['chunk_count']} chunks from URL.")
                    else:
                        st.error(f"Ingestion error: {resp.text}")
                except Exception as e:
                    st.error(f"Error: {e}")

    st.markdown("---")
    st.markdown("**Architecture Highlights:**")
    st.markdown("- 🧠 **LangGraph** Self-RAG Loop")
    st.markdown("- ⚡ **Qdrant** Dense Vector DB")
    st.markdown("- 🔍 **BM25 + RRF** Hybrid Search")
    st.markdown("- 🎯 **Cross-Encoder / Cohere** Reranking")
    st.markdown("- 🛡️ **DeBERTa-v3** NLI Hallucination Guard")


# Main UI Header
st.markdown('<div class="main-header">🧠 PASHA-NEURO-RAG</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Enterprise Self-Correcting Autonomous RAG Platform | Created by Mohammad Subhan Pasha</div>', unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I am PASHA-NEURO-RAG. Ask any question based on your uploaded enterprise documents.",
            "citations": [],
            "grounded": True,
            "groundedness_score": 1.0,
            "critique_score": 1.0
        }
    ]

# Display conversation history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("citations"):
            st.markdown("---")
            col1, col2, col3 = st.columns([2, 2, 3])
            with col1:
                if msg.get("grounded"):
                    st.markdown(f'<span class="grounded-badge-success">🛡️ Grounded ({msg.get("groundedness_score", 0)*100:.0f}%)</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="grounded-badge-warning">⚠️ Ungrounded ({msg.get("groundedness_score", 0)*100:.0f}%)</span>', unsafe_allow_html=True)
            with col2:
                st.markdown(f"**Self-RAG Score:** `{msg.get('critique_score', 0):.2f}`")

            st.markdown("**Sources & Citations:**")
            for cit in msg.get("citations", []):
                st.markdown(f'<span class="citation-badge">📌 {cit["source_name"]} (Relevance: {cit["relevance_score"]:.2f})</span>', unsafe_allow_html=True)
                with st.expander(f"View Chunk snippet [{cit['source_name']}]"):
                    st.caption(cit["snippet"])

# User Chat Input
if prompt := st.chat_input("Ask a question about enterprise architecture, policies, or specs..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        citations = []
        is_grounded = True
        groundedness_score = 0.0
        critique_score = 0.0

        with st.spinner("Executing Self-RAG Retrieval & Hallucination Guard..."):
            try:
                resp = requests.post(
                    f"{API_BASE_URL}/chat",
                    json={"query": prompt, "stream": False},
                    timeout=60
                )
                if resp.status_code == 200:
                    data = resp.json()
                    full_response = data["answer"]
                    citations = data.get("citations", [])
                    is_grounded = data.get("is_grounded", True)
                    groundedness_score = data.get("groundedness_score", 0.0)
                    critique_score = data.get("critique_score", 0.0)
                    message_placeholder.markdown(full_response)
                else:
                    full_response = "I encountered an error querying the backend system."
                    message_placeholder.markdown(full_response)
            except Exception as e:
                full_response = f"Backend API Connection Error: {e}"
                message_placeholder.markdown(full_response)

        st.session_state.messages.append({
            "role": "assistant",
            "content": full_response,
            "citations": citations,
            "grounded": is_grounded,
            "groundedness_score": groundedness_score,
            "critique_score": critique_score
        })
        st.rerun()
