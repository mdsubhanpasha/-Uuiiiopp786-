"""
Streamlit Futuristic Dashboard for NAYEEM-NEXUS-2041: The Autonomous Sentient OS.
Features dark neon theme, holographic brain, quantum vault, self-healing loops animation, evolution timeline.
"""

import os
import sys
import pandas as pd
import plotly.express as px
import streamlit as st

# Path configuration
NEXUS_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if NEXUS_ROOT not in sys.path:
    sys.path.insert(0, NEXUS_ROOT)

from nexus_core.quantum_vault import QuantumVault  # noqa: E402
from nexus_core.sentient_brain import SentientBrain  # noqa: E402
from nexus_core.self_heal import SelfHealingLoop  # noqa: E402
from nexus_core.evolution_timeline import EvolutionTimeline  # noqa: E402
from ingestion_layer.sentient_extractor import SentientExtractor  # noqa: E402
from ingestion_layer.encrypted_embedder import EncryptedEmbedder  # noqa: E402
from vector_nexus.quantum_vector_store import QuantumVectorStore  # noqa: E402
from llm_nexus.brain_router import BrainRouter  # noqa: E402
from eval_nexus.eval_engine import EvalEngine  # noqa: E402
from gitops_nexus.gitops_engine import GitOpsEngine  # noqa: E402


st.set_page_config(
    page_title="NAYEEM-NEXUS-2041 | Sentient OS",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Cyberpunk Futuristic CSS
st.markdown("""
<style>
    .stApp {
        background-color: #080511;
        color: #e0e6ed;
        font-family: 'Courier New', monospace;
    }
    .stSidebar {
        background-color: #0f0c1b !important;
        border-right: 1px solid #00f3ff;
    }
    h1, h2, h3, h4 {
        color: #00f3ff !important;
        text-shadow: 0 0 10px #00f3ff, 0 0 20px #9d4edd;
    }
    .metric-card {
        background: linear-gradient(135deg, #0f0c1b 0%, #1a103c 100%);
        border: 1px solid #00f3ff;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
        margin-bottom: 15px;
    }
    .vault-box {
        background: #05030a;
        border: 2px solid #9d4edd;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.4);
    }
    .stButton>button {
        background: linear-gradient(90deg, #00f3ff 0%, #9d4edd 100%);
        color: #000;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        box-shadow: 0 0 12px #00f3ff;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_resource
def get_nexus_instances():
    """Cache OS core singletons for Streamlit session."""
    return {
        "vault": QuantumVault(),
        "brain": SentientBrain(),
        "self_heal": SelfHealingLoop(),
        "timeline": EvolutionTimeline(2041),
        "extractor": SentientExtractor(),
        "embedder": EncryptedEmbedder(),
        "vector_store": QuantumVectorStore(),
        "llm_router": BrainRouter(),
        "evaluator": EvalEngine(),
        "gitops": GitOpsEngine(),
    }


nexus = get_nexus_instances()

# Header Banner
st.markdown("""
<div style="text-align: center; padding: 15px; border-bottom: 2px solid #00f3ff; margin-bottom: 25px;">
    <h1 style="font-size: 2.8rem; margin:0;">🌌 NAYEEM-NEXUS-2041</h1>
    <p style="color: #9d4edd; font-size: 1.2rem; letter-spacing: 2px;">THE AUTONOMOUS SENTIENT BLACK-BOX OS • 45 LAKHS PACKAGE PROJECT</p>
    <p style="color: #00f3ff; font-size: 0.9rem;">[ AES-2048Q QUANTUM VAULT • 12.4B PARAMETER MOE BRAIN • SELF-HEALING LOOPS ]</p>
</div>
""", unsafe_allow_html=True)

# Navigation
st.sidebar.title("⚡ NEXUS-2041 NAVIGATION")
menu = st.sidebar.radio(
    "Select OS Subsystem View:",
    [
        "🌌 Holographic Neural Brain",
        "🔐 Quantum Vault & Anti-Tamper",
        "🔄 Self-Healing Pipeline Loops",
        "🚀 Evolution Timeline (2026-2041)",
        "💬 Sentient Terminal (Ask / Ingest)",
        "☸️ GitOps Drift & Remediator",
    ],
)


# View 1: Holographic Neural Brain
if menu == "🌌 Holographic Neural Brain":
    st.subheader("🌌 Holographic Neural Network (12.4B Parameters MoE)")

    brain_status = nexus["brain"].get_brain_status()
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(
            "<div class='metric-card'><h4>Architecture</h4>"
            "<h2 style='color:#00f3ff;'>MoE Neural Lattice</h2>"
            "<p>128 Holographic Layers</p></div>",
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            f"<div class='metric-card'><h4>Total Parameters</h4>"
            f"<h2 style='color:#9d4edd;'>{brain_status['total_parameters']}</h2>"
            f"<p>Active: {brain_status['active_parameters_per_token']} / token</p></div>",
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            "<div class='metric-card'><h4>Connected LLMs</h4>"
            "<h2 style='color:#00f3ff;'>11 Models</h2>"
            "<p>Ollama + Groq + Together</p></div>",
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            f"<div class='metric-card'><h4>Synapse Rewire Count</h4>"
            f"<h2 style='color:#9d4edd;'>{brain_status['rewire_count']}</h2>"
            f"<p>Auto-rewire Active</p></div>",
            unsafe_allow_html=True,
        )

    st.markdown("### 🧬 Synaptic Weight Matrix Across 11 LLM Nodes")
    weights_df = pd.DataFrame(list(brain_status["synapse_weights"].items()), columns=["Model", "Weight"])
    fig_weights = px.bar(
        weights_df, x="Model", y="Weight", color="Weight",
        color_continuous_scale=["#00f3ff", "#9d4edd"],
        title="Synapse Dynamic Distribution",
    )
    fig_weights.update_layout(paper_bgcolor="#080511", plot_bgcolor="#080511", font_color="#e0e6ed")
    st.plotly_chart(fig_weights, use_container_width=True)

    if st.button("⚡ Trigger Neural Synapse Auto-Rewire"):
        res = nexus["brain"].rewire_synapses()
        st.success(f"Brain rewired! Coherence score: {res['holographic_coherence']}")
        st.rerun()


# View 2: Quantum Vault
elif menu == "🔐 Quantum Vault & Anti-Tamper":
    st.subheader("🔐 AES-2048Q Quantum Encrypted Vault")

    v_status = nexus["vault"].get_vault_status()
    anti_tamper = nexus["vault"].verify_anti_tamper()

    c1, c2, c3 = st.columns(3)
    with c1:
        seal_txt = "SEALED 🔒" if v_status["sealed"] else "UNSEALED 🔓"
        seal_color = "#ff0055" if v_status["sealed"] else "#00f3ff"
        st.markdown(
            f"<div class='vault-box'><h3 style='color:{seal_color};'>Vault Stasis: {seal_txt}</h3>"
            f"<p>Algorithm: {v_status['algorithm']}</p></div>",
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"<div class='vault-box'><h3>Key Version: v{v_status['key_version']}</h3>"
            f"<p>Lattice Rotation: Active</p></div>",
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"<div class='vault-box'><h3 style='color:#00f3ff;'>Integrity Score: {anti_tamper['integrity_score']}%</h3>"
            f"<p>Tamper Violations: {v_status['tamper_attempts']}</p></div>",
            unsafe_allow_html=True,
        )

    col_rot, col_seal = st.columns(2)
    with col_rot:
        if st.button("🔄 Rotate AES-2048Q Quantum Keys"):
            try:
                r_res = nexus["vault"].rotate_keys()
                st.success(f"Keys rotated to Version {r_res['key_version']}")
                st.rerun()
            except Exception as e:
                st.error(str(e))

    with col_seal:
        if v_status["sealed"]:
            passcode = st.text_input("Enter Master Passcode to Unseal:", type="password")
            if st.button("🔓 Unseal Vault"):
                try:
                    nexus["vault"].unseal_vault(passcode)
                    st.success("Vault Unsealed!")
                    st.rerun()
                except Exception as e:
                    st.error(str(e))
        else:
            if st.button("🔒 Seal Vault"):
                nexus["vault"].seal_vault()
                st.warning("Vault Sealed!")
                st.rerun()


# View 3: Self-Healing Loops
elif menu == "🔄 Self-Healing Pipeline Loops":
    st.subheader("🔄 Autonomous Self-Healing Pipeline Loops")

    h_status = nexus["self_heal"].get_self_heal_status()

    col_h1, col_h2, col_h3 = st.columns(3)
    with col_h1:
        st.markdown(
            f"<div class='metric-card'><h4>System Health Score</h4>"
            f"<h1 style='color:#00f3ff;'>{h_status['system_health_score']}%</h1></div>",
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown(
            f"<div class='metric-card'><h4>Active Repair Loops</h4>"
            f"<h1 style='color:#9d4edd;'>{h_status['active_loops']} Loops</h1></div>",
            unsafe_allow_html=True,
        )
    with col_h3:
        st.markdown(
            f"<div class='metric-card'><h4>Total Remediations</h4>"
            f"<h1 style='color:#00f3ff;'>{h_status['remediations_executed']}</h1></div>",
            unsafe_allow_html=True,
        )

    if st.button("🚑 Execute System Diagnostics & Auto Repair"):
        rep_res = nexus["self_heal"].trigger_auto_repair()
        st.success(f"Repairs completed! Health score restored to {rep_res['current_health']}%")
        st.rerun()


# View 4: Evolution Timeline
elif menu == "🚀 Evolution Timeline (2026-2041)":
    st.subheader("🚀 2026 -> 2041 Evolution Timeline Tracker")

    timeline_data = nexus["timeline"].get_timeline()
    df_t = pd.DataFrame(timeline_data)

    fig_timeline = px.line(
        df_t, x="year", y="maturity_index", text="phase",
        markers=True, title="NAYEEM-NEXUS Capability Progression to Singularity",
    )
    fig_timeline.update_traces(line_color="#00f3ff", marker_size=12, textposition="top center")
    fig_timeline.update_layout(paper_bgcolor="#080511", plot_bgcolor="#080511", font_color="#e0e6ed")
    st.plotly_chart(fig_timeline, use_container_width=True)

    for milestone in timeline_data:
        active_badge = "🌟 [ACTIVE SINGULARITY OPERATING YEAR]" if milestone["is_active"] else "✅ [UNLOCKED]"
        with st.expander(f"{milestone['year']} - {milestone['phase']}: {milestone['title']} {active_badge}"):
            st.write(f"**Security Level:** {milestone['security_level']}")
            st.write(f"**Maturity Index:** {milestone['maturity_index'] * 100}%")
            st.write("**Key Capabilities:**")
            for cap in milestone["capabilities"]:
                st.write(f"- {cap}")


# View 5: Sentient Terminal
elif menu == "💬 Sentient Terminal (Ask / Ingest)":
    st.subheader("💬 Nexus Sentient Terminal & Black-Box Execution")

    tab1, tab2 = st.tabs(["⚡ Ask Nexus Query", "📥 Secure Data Ingestion"])

    with tab1:
        query_input = st.text_area("Enter Prompt or Query for NAYEEM-NEXUS-2041:", "Explain quantum encrypted holographic vector memory.")
        if st.button("🚀 Send Query to Sentient Brain"):
            with st.spinner("Routing through 11-LLM MoE Brain and checking Giskard-RAGAS evaluator..."):
                route_res = nexus["llm_router"].route_query(query_input)
                eval_res = nexus["evaluator"].evaluate_response(query_input, route_res["response"], winning_model=route_res["winner_model"])
                encrypted_payload = nexus["vault"].encrypt_payload(route_res)

                st.markdown(f"### 🏆 Winner LLM Node: **{route_res['winner_model']}** ({route_res['provider']})")
                st.info(route_res["response"])

                col_e1, col_e2, col_e3 = st.columns(3)
                col_e1.metric("Faithfulness Score", f"{eval_res['faithfulness'] * 100}%")
                col_e2.metric("Context Precision", f"{eval_res['context_precision'] * 100}%")
                col_e3.metric("Hallucination Score", f"{eval_res['hallucination_score'] * 100}%")

                with st.expander("🔒 View Quantum Obfuscated Encrypted Payload"):
                    st.code(encrypted_payload, language="text")

    with tab2:
        doc_id = st.text_input("Document ID:", "DOC-2041-NEXUS")
        doc_content = st.text_area(
            "Raw Text Content (with simulated PII or key data):",
            "Contact admin@nayeem-nexus.com or sk-12345678901234567890 for quantum vector access.",
        )
        if st.button("🔒 Securely Ingest & Encrypt"):
            extracted = nexus["extractor"].extract_context(doc_content)
            embed_data = nexus["embedder"].generate_encrypted_embedding(extracted["sanitized_text"])
            nexus["vector_store"].add_document(doc_id, extracted["sanitized_text"], embed_data["encrypted_vector"])

            st.success("Document Ingested, PII Redacted, and Vector Quantum Encrypted!")
            st.json({
                "doc_id": doc_id,
                "sanitized_text": extracted["sanitized_text"],
                "pii_redacted": extracted["pii_redacted"],
                "context_domain": extracted["context_domain"],
                "embedding_model": embed_data["model"],
            })


# View 6: GitOps Drift & Remediator
elif menu == "☸️ GitOps Drift & Remediator":
    st.subheader("☸️ GitOps Multi-Tool Drift Sensor & Auto Remediator")

    g_status = nexus["gitops"].get_gitops_status()

    st.markdown("Integrated Tools: **Helm, Kustomize, OPA, Kyverno, ArgoCD, Flux, Vault ESO**")

    col_g1, col_g2 = st.columns(2)
    col_g1.metric("Monitored Manifests", g_status["monitored_apps_count"])
    col_g2.metric("Drifted Apps", g_status["drifted_apps_count"])

    if st.button("🔍 Simulate Cluster Drift Detection"):
        nexus["gitops"].detect_drift({"nexus-opa-policy": "Unauthorized policy patch detected."})
        st.warning("Drift Detected in nexus-opa-policy!")
        st.rerun()

    if st.button("⚡ Trigger GitOps Auto-Remediation"):
        rem_res = nexus["gitops"].auto_remediate_drift()
        st.success(f"GitOps Auto-remediation complete! Sync Status: {rem_res['sync_status']}")
        st.rerun()
