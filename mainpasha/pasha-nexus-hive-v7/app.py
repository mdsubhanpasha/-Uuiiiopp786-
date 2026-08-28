"""
PASHA-NEXUS-HIVE V7 - Streamlit Futuristic Dark UI
Features:
- Neon Cyan (#00F0FF) & Purple theme
- Glassmorphism CSS layout
- CSS Hive Animation
- 4 Pages: Job Hunter, Resume Studio (Side-by-side diff + Circular ATS score meter), Pipeline Kanban, Interview Prep (Voice practice mock)
"""
import streamlit as st
import time
import os
import sys

# Add path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from agents.orchestrator import SwarmOrchestrator
from core.job_scraper import JobScraper
from core.resume_tailor import ResumeTailor, DEFAULT_BASE_RESUME
from core.cover_letter_gen import CoverLetterGenerator
from core.cold_email_gen import ColdEmailGenerator
from core.interview_prep import InterviewPrepEngine
from dashboard.analytics import WorkforceAnalytics

# Page config
st.set_page_config(
    page_title="PASHA-NEXUS-HIVE V7 | Autonomous AI Workforce Swarm",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Futuristic Dark Neon Glassmorphism CSS & Hive Animation
custom_css = """
<style>
/* Main theme background */
.stApp {
    background: radial-gradient(circle at 50% 10%, #0d0f1d 0%, #05060b 100%);
    color: #e0f7fc;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
}

/* Glassmorphism containers */
div.css-card, div[data-testid="stVerticalBlock"] > div.element-container {
    background: rgba(13, 15, 29, 0.65);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(0, 240, 255, 0.2);
    border-radius: 12px;
    padding: 12px;
    box-shadow: 0 8px 32px 0 rgba(0, 240, 255, 0.08);
}

/* Glowing Neon Cyan headers */
h1, h2, h3, .neon-text {
    color: #00F0FF !important;
    text-shadow: 0 0 10px rgba(0, 240, 255, 0.5), 0 0 20px rgba(0, 240, 255, 0.3);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #00F0FF 0%, #7B2CBF 100%) !important;
    color: #ffffff !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 8px !important;
    box-shadow: 0 4px 15px rgba(0, 240, 255, 0.4) !important;
    transition: all 0.3s ease !important;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(0, 240, 255, 0.7) !important;
}

/* Hive Hexagon CSS Animation */
.hive-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 15px 0;
}

.hexagon {
    width: 40px;
    height: 23px;
    background-color: #00F0FF;
    position: relative;
    display: inline-block;
    margin: 5px;
    box-shadow: 0 0 12px #00F0FF;
    animation: pulse 2s infinite ease-in-out;
}

.hexagon:before, .hexagon:after {
    content: "";
    position: absolute;
    width: 0;
    border-left: 20px solid transparent;
    border-right: 20px solid transparent;
}

.hexagon:before {
    bottom: 100%;
    border-bottom: 11.5px solid #00F0FF;
}

.hexagon:after {
    top: 100%;
    width: 0;
    border-top: 11.5px solid #00F0FF;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); opacity: 0.8; }
    50% { transform: scale(1.15); opacity: 1; filter: drop-shadow(0 0 15px #7B2CBF); }
}

/* Circular ATS Gauge Meter */
.circle-gauge {
    position: relative;
    width: 130px;
    height: 130px;
    border-radius: 50%;
    background: conic-gradient(#00F0FF calc(var(--score) * 1%), rgba(255,255,255,0.1) 0);
    display: flex;
    justify-content: center;
    align-items: center;
    margin: 0 auto;
    box-shadow: 0 0 20px rgba(0,240,255,0.4);
}

.circle-gauge::before {
    content: "";
    position: absolute;
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: #0d0f1d;
}

.circle-score {
    position: relative;
    z-index: 2;
    font-size: 28px;
    font-weight: 800;
    color: #00F0FF;
}
</style>
"""

st.markdown(custom_css, unsafe_allow_html=True)

# Helper instances
@st.cache_resource
def get_orchestrator():
    return SwarmOrchestrator()

@st.cache_resource
def get_analytics():
    return WorkforceAnalytics()

orchestrator = get_orchestrator()
analytics = get_analytics()
tailorer = ResumeTailor()
cl_gen = CoverLetterGenerator()
ce_gen = ColdEmailGenerator()
ip_engine = InterviewPrepEngine()

# Sidebar Navigation
st.sidebar.markdown("## ⚡ NEXUS-HIVE V7")
st.sidebar.markdown("### Autonomous AI Workforce Swarm")

# Hive animation in sidebar
st.sidebar.markdown("""
<div class="hive-container">
    <div class="hexagon"></div>
    <div class="hexagon" style="animation-delay: 0.3s; background-color: #7B2CBF;"></div>
    <div class="hexagon" style="animation-delay: 0.6s;"></div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio(
    "Select Division Page",
    ["🎯 Job Hunter Swarm", "📄 Resume Studio", "📊 Pipeline Kanban", "🎙️ Interview Prep & Voice Mock"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Swarm Status:** 🟢 100 Active AI Workers")
st.sidebar.markdown("**Target Role:** Remote AI Engineer ($78k+)")
st.sidebar.markdown("**Past OS Powered:** PASHA-OS, NEURO-RAG, VOX-AI, PASHA-UNIFIED-OS, AUTO-GROWTH, PASHA-GLASS")


# ---------------------------------------------------------
# PAGE 1: JOB HUNTER SWARM
# ---------------------------------------------------------
if page == "🎯 Job Hunter Swarm":
    st.markdown("<h1>🎯 Autonomous Job Hunter Swarm</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a0aec0;'>Execute 6-node LangGraph Swarm (Scrape -> Research -> Tailor -> Generate -> Critic -> Tracker)</p>", unsafe_allow_html=True)

    col1, col2 = st.columns([2, 1])

    with col1:
        input_type = st.radio("Input Source", ["Raw Job Description Text", "Job Posting URL"], horizontal=True)
        jd_input = st.text_area(
            "Paste Job Description or URL",
            height=220,
            placeholder="e.g. Perplexity Staff AI Engineer - $120,000 Remote. Requirements: LangGraph, Qdrant, FastAPI, Docker..."
        )

        run_btn = st.button("🚀 Launch 100 AI Employee Swarm")

    with col2:
        st.markdown("### ⚡ Swarm Metrics")
        metrics = analytics.get_summary_metrics()
        st.metric("Daily Application Capacity", f"{metrics['daily_capacity']} / day")
        st.metric("Avg ATS Compatibility", f"{metrics['avg_ats_score']}%")
        st.metric("Response Rate", metrics['response_rate'])
        st.metric("Weekly Hours Saved", f"{metrics['hours_saved_weekly']} hrs")

    if run_btn:
        if not jd_input.strip():
            st.warning("Please enter a job description or URL.")
        else:
            with st.spinner("⚡ Swarm active: Scraping -> Researching Company -> Tailoring Resume -> Generating Documents -> Evaluating Critic Loop..."):
                start_time = time.time()
                res = orchestrator.run_swarm(jd_input, is_url=(input_type == "Job Posting URL"))
                elapsed = round(time.time() - start_time, 2)

            st.success(f"✅ Swarm Execution Complete in {elapsed}s! Application ID: {res['application_id']}")

            # Display outputs
            st.markdown("---")
            st.markdown("### 📋 Swarm Generated Artifacts")

            t1, t2, t3, t4 = st.tabs(["📄 Tailored Resume", "✉️ Cover Letter", "📧 Cold Email", "🕵️ Company Intelligence"])

            with t1:
                st.write("**ATS Compatibility Score:**", res["tailored_resume"].get("ats_score"), "/ 100")
                st.json(res["tailored_resume"])
                if res.get("pdf_path") and os.path.exists(res["pdf_path"]):
                    with open(res["pdf_path"], "rb") as pdf_file:
                        st.download_button("📥 Download ATS Tailored Resume PDF", pdf_file, file_name=f"Resume_{res['application_id']}.pdf")

            with t2:
                st.text_area("Generated Cover Letter", res["cover_letter"], height=280)

            with t3:
                ce = res["cold_email"]
                st.write("**Subject:**", ce.get("subject"))
                st.text_area("Cold Email Body", ce.get("body"), height=180)

            with t4:
                st.json(res["company_research"])


# ---------------------------------------------------------
# PAGE 2: RESUME STUDIO
# ---------------------------------------------------------
elif page == "📄 Resume Studio":
    st.markdown("<h1>📄 AI Resume Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a0aec0;'>Side-by-side diff comparison & real-time circular ATS score meter.</p>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 1, 1])

    with c1:
        st.markdown("### 📝 Base Baseline Resume")
        st.text_area("Base Experience", "\n".join(DEFAULT_BASE_RESUME["experience"][0]["bullets"]), height=220)

    with c2:
        st.markdown("### 🎯 Target Role Parameters")
        target_role = st.text_input("Target Job Title", "Staff AI Engineer")
        target_company = st.text_input("Target Company", "Perplexity AI")
        keywords_str = st.text_input("Target Keywords (comma separated)", "LangGraph, Qdrant, FastAPI, PyTorch, RAG")
        keywords_list = [k.strip() for k in keywords_str.split(",") if k.strip()]

        tailor_btn = st.button("⚡ Generate Tailored STAR Bullets")

    with c3:
        st.markdown("### 📊 ATS Score Meter")
        if 'tailored_res' in st.session_state:
            score = st.session_state['tailored_res'].get('ats_score', 96)
        else:
            score = 96

        st.markdown(f"""
        <div class="circle-gauge" style="--score: {score};">
            <div class="circle-score">{score}%</div>
        </div>
        <p style="text-align:center; color:#00F0FF; margin-top:10px;">ATS Match: High Match (>95%)</p>
        """, unsafe_allow_html=True)

    if tailor_btn or 'tailored_res' in st.session_state:
        if tailor_btn:
            jd_info = {"title": target_role, "company": target_company, "keywords": keywords_list}
            st.session_state['tailored_res'] = tailorer.tailor_resume(jd_info)

        res_data = st.session_state['tailored_res']

        st.markdown("---")
        st.markdown("### 🔄 Side-by-Side Bullet Diff & STAR Rewriter")

        diff_col1, diff_col2 = st.columns(2)
        with diff_col1:
            st.markdown("#### Baseline Resume Bullets")
            for bullet in DEFAULT_BASE_RESUME["experience"][0]["bullets"]:
                st.info(f"• {bullet}")

        with diff_col2:
            st.markdown("#### STAR + 6 OS Metrics Rewritten Bullets")
            for bullet in res_data["experience"][0]["bullets"]:
                st.success(f"• {bullet}")


# ---------------------------------------------------------
# PAGE 3: PIPELINE KANBAN & ANALYTICS
# ---------------------------------------------------------
elif page == "📊 Pipeline Kanban":
    st.markdown("<h1>📊 Swarm Application Pipeline & Kanban</h1>", unsafe_allow_html=True)

    st.markdown("### 🏆 Real-Time Conversion Analytics")
    k1, k2, k3, k4 = st.columns(4)
    metrics = analytics.get_summary_metrics()
    k1.metric("Total Swarm Applications", metrics["total_applications"])
    k2.metric("Recruiter Response Rate", metrics["response_rate"], "+4.2%")
    k3.metric("Interviews Scheduled", metrics["interviews_booked"])
    k4.metric("Remote Offers Received", metrics["remote_offers"], "$85k-$140k")

    st.markdown("---")

    g1, g2 = st.columns(2)
    with g1:
        st.plotly_chart(analytics.generate_pipeline_funnel(), use_container_width=True)
    with g2:
        st.plotly_chart(analytics.generate_ats_score_distribution(), use_container_width=True)

    st.markdown("### 📌 Kanban Application Pipeline")
    kb1, kb2, kb3, kb4 = st.columns(4)

    with kb1:
        st.markdown("#### 📥 Applied (42)")
        st.caption("• Anthropic - Senior RAG Engineer ($130k)")
        st.caption("• Scale AI - Workforce Engineer ($95k)")
        st.caption("• Cohere - Agent Engineer ($110k)")

    with kb2:
        st.markdown("#### 💬 Recruiter Screen (14)")
        st.caption("• Perplexity - Staff AI Engineer ($120k)")
        st.caption("• Vercel - Remote AI Systems ($85k)")
        st.caption("• Cursor - Swarm Architect ($125k)")

    with kb3:
        st.markdown("#### 🎯 Tech Deep-Dive (8)")
        st.caption("• OpenAI - Lead AI Architect ($140k)")
        st.caption("• Pinecone - Vector RAG Engineer ($115k)")

    with kb4:
        st.markdown("#### 🥳 Remote Offer (4)")
        st.caption("• Top AI MNC - Remote Principal ($128k)")
        st.caption("• AI Workforce Corp - Remote Staff ($95k)")


# ---------------------------------------------------------
# PAGE 4: INTERVIEW PREP & VOICE MOCK
# ---------------------------------------------------------
elif page == "🎙️ Interview Prep & Voice Mock":
    st.markdown("<h1>🎙️ AI Technical Interview & Voice Mock Simulator</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#a0aec0;'>Practice STAR behavioral & technical AI questions with voice transcript evaluation.</p>", unsafe_allow_html=True)

    questions = ip_engine.generate_interview_questions({"company": "Perplexity", "title": "Staff AI Engineer"})

    q_titles = [f"Q{i+1}: {q['category']} - {q['question'][:50]}..." for i, q in enumerate(questions)]
    selected_idx = st.selectbox("Select Interview Question Flashcard", range(len(questions)), format_func=lambda i: q_titles[i])

    selected_q = questions[selected_idx]

    st.markdown("---")
    st.markdown(f"### ❓ Question: {selected_q['question']}")

    with st.expander("💡 View Model STAR Benchmark Answer"):
        st.write(selected_q["star_answer"])

    st.markdown("---")
    st.markdown("### 🎤 Voice Mock Practice Simulator")
    st.write("Speak or type your answer transcript below to receive immediate AI score and feedback:")

    user_transcript = st.text_area(
        "Spoken Response Transcript",
        height=140,
        placeholder="In my previous role at PASHA-OS, I architected a 25-agent MNC simulation using LangGraph resulting in sub-800ms API latency..."
    )

    eval_btn = st.button("⚡ Submit Spoken Response for Evaluation")

    if eval_btn:
        if not user_transcript.strip():
            st.warning("Please enter your spoken transcript first.")
        else:
            eval_res = ip_engine.simulate_voice_mock_response(selected_q['question'], user_transcript)
            st.markdown("#### 🎯 Voice Response Evaluation")

            ev_col1, ev_col2 = st.columns([1, 2])
            with ev_col1:
                st.metric("STAR Confidence Score", f"{eval_res['score']} / 100")
                st.write("**STAR Alignment:**", eval_res["star_alignment"])
            with ev_col2:
                st.info(f"**Feedback:** {eval_res['feedback']}")
