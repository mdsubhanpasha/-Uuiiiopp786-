"""Streamlit Executive Command Center Dashboard for PASHA-OS V2 Enterprise 20-Agent MNC Operating System."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from fpdf import FPDF

from core.orchestration import PashaOrchestrator

# Page configuration
st.set_page_config(
    page_title="PASHA-OS V2 | Enterprise 20-Agent MNC Operating System",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark theme custom CSS
st.markdown(
    """
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .stMetric { background-color: #1E222D; padding: 15px; border-radius: 10px; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #0066CC; color: white; font-weight: bold; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PASHA-OS V2: Enterprise 20-Agent Autonomous MNC Operating System")
st.caption("FAANG-Grade Autonomous MNC Operating System • 20 AI Agents • Real-time Research • LangGraph Meeting Engine")

orchestrator = PashaOrchestrator()

# Sidebar Executive Controls
st.sidebar.header("Executive Command & Parameters")
company_name = st.sidebar.text_input("MNC Entity Name", "Acme Global Enterprise Inc.")
cash_reserve = st.sidebar.number_input("Liquid Cash Balance ($)", min_value=100000.0, value=5000000.0, step=500000.0)
contract_input = st.sidebar.text_area(
    "Contract Audit Text",
    "This agreement includes unlimited liability indemnification and offshore governing law jurisdiction.",
)

st.sidebar.markdown("---")
st.sidebar.header("Department Meetings Engine")
meeting_choice = st.sidebar.selectbox(
    "Select Meeting Protocol",
    [
        "Monthly Board Meeting",
        "Daily Standup (All 20 Agents)",
        "Weekly Engineering Meeting",
        "Weekly Data & AI Meeting",
        "Weekly Product & Growth Meeting",
        "Weekly Customer & Sales Meeting",
    ],
)

if st.sidebar.button("Run Enterprise Meeting"):
    st.session_state["run_meeting"] = True

# Execute Master Enterprise Analysis
data = orchestrator.run_full_enterprise_analysis(
    {
        "historical_cashflows": [120000, 115000, 110000, 105000, 98000],
        "contract_text": contract_input,
    }
)

decision = data["ceo_decision"]
risk_score = data["overall_risk_score"]
cfo_data = data["agents_summary"]["cfo"]
cmo_data = data["agents_summary"]["cmo"]
coo_data = data["agents_summary"]["coo"]
chro_data = data["agents_summary"]["chro"]
legal_data = data["agents_summary"]["legal"]
divisions = data["divisions_summary"]

# Top Row: Executive Key Metrics
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("Aggregated Risk Index")
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_score * 100,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Enterprise Risk (%)"},
            gauge={
                "axis": {"range": [0, 100]},
                "bar": {"color": "#FF4B4B" if risk_score > 0.7 else "#00CC66"},
                "steps": [
                    {"range": [0, 30], "color": "#1E3A2B"},
                    {"range": [30, 70], "color": "#3A331E"},
                    {"range": [70, 100], "color": "#3A1E1E"},
                ],
            },
        )
    )
    fig_gauge.update_layout(paper_bgcolor="#161B22", font={"color": "white"}, height=200, margin=dict(t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.subheader("High-Precision Cashflow Forecast (Decimal)")
    forecast_df = pd.DataFrame(
        {"Month": [f"M{i+1}" for i in range(len(cfo_data["forecast"]))], "Cashflow": cfo_data["forecast"]}
    )
    fig_line = px.line(forecast_df, x="Month", y="Cashflow", markers=True)
    fig_line.update_layout(paper_bgcolor="#161B22", plot_bgcolor="#161B22", font={"color": "white"}, height=200)
    st.plotly_chart(fig_line, use_container_width=True)

with col3:
    st.subheader("Runway & Unit Economics")
    st.metric(label="Cash Runway", value=f"{cfo_data['runway_months']} Months")
    ue = cfo_data.get("unit_economics", {})
    st.metric(label="LTV / CAC Ratio", value=f"{ue.get('ltv_cac_ratio', 6.0)}x", delta="Healthy > 3.0x")

st.markdown("---")

# Row 2: CEO Board Decision
st.subheader("LangGraph CEO Strategy Execution")
if decision == "HALT_EXPANSION":
    st.error(f"🚨 CEO BOARD DECISION: {decision} (Enterprise Risk Score: {risk_score:.2f})")
else:
    st.success(f"🚀 CEO BOARD DECISION: {decision} (Enterprise Risk Score: {risk_score:.2f})")

st.markdown("---")

# Row 3: 20 Agents Display across 5 Divisions
st.subheader("20 Autonomous MNC Agents across 5 Divisions")

tabs = st.tabs([
    "🏛️ Core C-Suite (7)",
    "💻 Engineering (4)",
    "📊 Data & AI (4)",
    "🚀 Product & Growth (3)",
    "🤝 Customer & Sales (2)",
    "🛡️ QA & Red Team (2)",
])

with tabs[0]:
    c_suite = divisions["CORE_C_SUITE"]
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("#### 👔 CEO Agent")
        st.write(f"**Decision:** {c_suite['ceo']}")
        st.markdown("#### 💵 CFO Agent (Decimal Engine)")
        st.write(f"**Runway:** {cfo_data['runway_months']} Months")
        st.write(f"**Health:** {cfo_data.get('financial_health')}")
    with col_b:
        st.markdown("#### 🛠️ CTO Agent")
        cto = c_suite["cto"]
        st.write(f"**Stack:** {cto.get('final_decision', {}).get('recommended_stack', {}).get('backend_framework')}")
        st.markdown("#### 📈 CMO Agent")
        st.write(f"**GTM ROI:** {c_suite['cmo'].get('extra_fields', {}).get('projected_roi_percent')}%")
    with col_c:
        st.markdown("#### 🚚 COO Agent")
        st.write(f"**Cost Min:** ${c_suite['coo'].get('optimal_cost', 0):,.2f}")
        st.markdown("#### 👥 CHRO Agent")
        st.write(f"**Turnover Risk:** {c_suite['chro'].get('workforce_health')}")
        st.markdown("#### ⚖️ CLO Agent")
        st.write(f"**Compliance:** {c_suite['clo_legal'].get('compliance_status')}")

with tabs[1]:
    eng = divisions["ENGINEERING_DIVISION"]
    e1, e2 = st.columns(2)
    with e1:
        st.markdown("#### 🏗️ Staff Engineer Agent")
        st.write(f"**Design:** {eng['staff_engineer'].get('final_decision')}")
        st.markdown("#### 🧪 QA Automation Agent")
        st.write(f"**Coverage Target:** {eng['qa_automation'].get('extra_fields', {}).get('coverage_target')}%")
    with e2:
        st.markdown("#### ☁️ DevOps/SRE Agent")
        st.write(f"**SLA Action:** {eng['devops_sre'].get('final_decision')}")
        st.markdown("#### 🛡️ Security Agent")
        st.write(f"**OWASP Audit:** {eng['security'].get('final_decision')}")

with tabs[2]:
    data_div = divisions["DATA_AND_AI_DIVISION"]
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("#### 🧪 Data Scientist Agent")
        ds_run = data_div['data_scientist'].get('extra_fields', {}).get('model_metrics', {}).get('mlflow_run_id')
        st.write(f"**MLflow Run:** {ds_run}")
        st.markdown("#### ⚙️ ML Engineer Agent")
        st.write(f"**Endpoint Status:** {data_div['ml_engineer'].get('final_decision', {}).get('deployment_status')}")
    with d2:
        st.markdown("#### 📈 Analytics Agent")
        st.write(f"**Health Index:** {data_div['analytics'].get('final_decision', {}).get('bi_health_index')}")
        st.markdown("#### 🔍 Research Agent")
        st.write("**Source:** Tavily / DuckDuckGo Real-Time Search Pipeline")

with tabs[3]:
    prod = divisions["PRODUCT_AND_GROWTH_DIVISION"]
    p1, p2 = st.columns(2)
    with p1:
        st.markdown("#### 📝 Product Manager Agent")
        st.write(f"**Top Priority:** {prod['product_manager'].get('final_decision', {}).get('top_priority_feature')}")
        st.markdown("#### 🎨 UX Research Agent")
        st.write(f"**A/B Test Winner:** {prod['ux_research'].get('final_decision', {}).get('winning_variant')}")
    with p2:
        st.markdown("#### 🚀 Growth Hacker Agent")
        st.write(f"**Viral K-Factor:** {prod['growth_hacker'].get('extra_fields', {}).get('viral_k_factor')}")

with tabs[4]:
    cust = divisions["CUSTOMER_AND_SALES_DIVISION"]
    s1, s2 = st.columns(2)
    with s1:
        st.markdown("#### 💼 Sales Strategist Agent")
        st.write(f"**Lead Score:** {cust['sales_strategist'].get('final_decision', {}).get('lead_score')}/100")
    with s2:
        st.markdown("#### ❤️ Customer Success Agent")
        st.write(f"**Account Health:** {cust['customer_success'].get('final_decision', {}).get('health_status')}")

with tabs[5]:
    qa_red = divisions["QUALITY_ASSURANCE_AND_RED_TEAM"]
    q1, q2 = st.columns(2)
    with q1:
        st.markdown("#### ✅ Validator Agent")
        val = qa_red.get("validator") or {}
        st.write(f"**Validation Status:** {val.get('final_decision', {}).get('validation_status', 'PASSED')}")
    with q2:
        st.markdown("#### 🚩 Critic Agent (Red Team)")
        crit = qa_red.get("critic") or {}
        st.write(f"**Flaw Severity:** {crit.get('final_decision', {}).get('severity', 'LOW')}")

st.markdown("---")

# Online Research Pipeline Drawer
st.subheader("Real-Time Online Research Pipeline (Tavily / DDG)")
research_query = st.text_input("Enter Topic for Real-Time MNC Research", "Enterprise AI Agent OS benchmarks 2025")
if st.button("Execute Online Research"):
    with st.spinner("Searching real-time web sources..."):
        res_output = orchestrator.research_agent.execute_deep_research(research_query)
        st.success(f"Source Used: {res_output['extra_fields']['primary_research']['source_used']}")
        st.write(f"**Synthesized Dossier:** {res_output['extra_fields']['synthesized_summary']}")

st.markdown("---")


def generate_pdf_report(company_name: str, decision: str, risk_score: float) -> bytes:
    """Generate executive PDF briefing for 20-Agent MNC system.

    Args:
        company_name (str): Corporate entity name.
        decision (str): Board decision outcome.
        risk_score (float): Calculated risk score.

    Returns:
        bytes: Raw PDF bytes.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, f"PASHA-OS V2 Board Briefing: {company_name}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, f"CEO Board Decision: {decision}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, f"Enterprise Risk Index: {risk_score:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(
        0,
        6,
        "This executive briefing is synthesized by PASHA-OS V2 Enterprise 20-Agent Autonomous MNC Operating System. "
        "Spanning Core C-Suite, Engineering, Data & AI, Product & Growth, Customer & Sales, and Red Team Quality "
        "Assurance.",
    )
    return pdf.output()


pdf_bytes = generate_pdf_report(company_name, decision, risk_score)
st.download_button(
    label="📄 Download 20-Agent Executive Briefing PDF",
    data=pdf_bytes,
    file_name=f"PASHA_OS_V2_{company_name.replace(' ', '_')}_Briefing.pdf",
    mime="application/pdf",
)
