"""Streamlit CEO Command Center Dashboard for PASHA-OS."""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from fpdf import FPDF

from core.orchestration import PashaOrchestrator

# Page setup
st.set_page_config(
    page_title="PASHA-OS | Autonomous CEO Enterprise Intelligence OS",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Dark theme custom CSS
st.markdown(
    """
    <style>
    .main { background-color: #0E1117; color: #FAFAFA; }
    .stMetric { background-color: #1E222D; padding: 15px; border-radius: 10px; }
    .css-1r6594q { background-color: #161B22; }
    .stButton>button { width: 100%; border-radius: 8px; background-color: #0066CC; color: white; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("PASHA-OS: Autonomous CEO Command Center")
st.caption("Predictive Autonomous System for Holistic Administration - Enterprise Intelligence OS")

orchestrator = PashaOrchestrator()

# Sidebar inputs
st.sidebar.header("Executive Parameters")
company_name = st.sidebar.text_input("Company Name", "Acme Enterprise Corp")
cash_reserve = st.sidebar.number_input("Cash Reserve ($)", min_value=100000.0, value=5000000.0, step=500000.0)
contract_input = st.sidebar.text_area(
    "Contract Audit Text",
    "This agreement includes unlimited liability indemnification and penalty clauses under offshore jurisdiction.",
)

if st.sidebar.button("Run CEO Decision Pipeline"):
    st.session_state["executed"] = True

# Execute analysis
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
investor_data = data["agents_summary"]["investor"]

# Row 1: Top Executive Metrics & Gauge
col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.subheader("Aggregated Enterprise Risk")
    fig_gauge = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=risk_score * 100,
            domain={"x": [0, 1], "y": [0, 1]},
            title={"text": "Risk Index (%)"},
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
    fig_gauge.update_layout(paper_bgcolor="#161B22", font={"color": "white"}, height=220, margin=dict(t=30, b=10))
    st.plotly_chart(fig_gauge, use_container_width=True)

with col2:
    st.subheader("Cashflow Forecast (12 Months)")
    forecast_df = pd.DataFrame(
        {"Month": [f"M{i+1}" for i in range(len(cfo_data["forecast"]))], "Cashflow": cfo_data["forecast"]}
    )
    fig_line = px.line(forecast_df, x="Month", y="Cashflow", markers=True)
    fig_line.update_layout(paper_bgcolor="#161B22", plot_bgcolor="#161B22", font={"color": "white"}, height=220)
    st.plotly_chart(fig_line, use_container_width=True)

with col3:
    st.subheader("Compliance & Runway Status")
    st.metric(label="Cash Runway", value=f"{cfo_data['runway_months']} Months")
    st.metric(
        label="Statutory Compliance",
        value=legal_data["compliance_status"],
        delta="-High Risk" if legal_data["risk_score"] > 0.5 else "Compliant",
    )

st.markdown("---")

# Row 2: CEO Board Decision Panel
st.subheader("CEO Board Decision Execution")
if decision == "HALT_EXPANSION":
    st.error(f"🚨 BOARD DECISION: {decision} (Enterprise Risk Score: {risk_score:.2f})")
else:
    st.success(f"🚀 BOARD DECISION: {decision} (Enterprise Risk Score: {risk_score:.2f})")

st.markdown("---")

# Row 3: All Agents Status Grid
st.subheader("7 C-Suite Autonomous Agent Signals")
grid1, grid2, grid3, grid4 = st.columns(4)

with grid1:
    st.markdown("### 💵 CFO Agent")
    st.write(f"**Financial Health:** {cfo_data['financial_health']}")
    st.write(f"**Runway:** {cfo_data['runway_months']} Months")

with grid2:
    st.markdown("### 📈 CMO Agent")
    st.write(f"**Market Position:** {cmo_data['overall_market_position']}")
    st.write(f"**Sentiment Score:** {cmo_data.get('sentiment_score', 0.6)}")

with grid3:
    st.markdown("### 🚚 COO Agent")
    st.write(f"**Optimal Supply Cost:** ${coo_data['optimal_cost']:,.2f}")
    st.write(f"**Solver Status:** {coo_data['status']}")

with grid4:
    st.markdown("### 👥 CHRO Agent")
    st.write(f"**Workforce Health:** {chro_data['workforce_health']}")
    st.write(f"**High Attrition Risk Employees:** {chro_data['high_risk_count']}")

grid5, grid6, grid7 = st.columns(3)
with grid5:
    st.markdown("### ⚖️ Legal Agent")
    st.write(f"**Risk Score:** {legal_data['risk_score']}")
    st.write(f"**Flagged Clauses:** {len(legal_data['flagged_clauses'])}")

with grid6:
    st.markdown("### 📊 Investor Agent")
    st.write(f"**ARR:** ${investor_data['arr_usd']:,.2f}")
    st.write(f"**Valuation:** ${investor_data['implied_valuation_usd']:,.2f}")

with grid7:
    st.markdown("### 🎲 Monte Carlo Risk Engine")
    mc = data["monte_carlo_metrics"]
    st.write(f"**95% VaR:** ${mc['var_95']:,.2f}")
    st.write(f"**95% CVaR:** ${mc['cvar_95']:,.2f}")

st.markdown("---")


# Executive PDF Download Generator
def generate_pdf_report(company_name: str, decision: str, risk_score: float) -> bytes:
    """Generate executive PDF report using FPDF2.

    Args:
        company_name (str): Corporate entity name.
        decision (str): LangGraph CEO decision outcome.
        risk_score (float): Calculated aggregated risk score.

    Returns:
        bytes: Raw PDF file byte stream.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 10, f"PASHA-OS Executive Board Briefing: {company_name}", new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"CEO Decision: {decision}", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Enterprise Risk Score: {risk_score:.2f}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(
        0,
        8,
        "This autonomous report is synthesized by PASHA-OS multi-agent system combining CFO, CMO, "
        "COO, CHRO, Legal, and Investor Agents with 50,000 iteration Monte Carlo risk simulations.",
    )
    return pdf.output()


pdf_bytes = generate_pdf_report(company_name, decision, risk_score)
st.download_button(
    label="📄 Download Executive Board PDF Report",
    data=pdf_bytes,
    file_name=f"PASHA_OS_{company_name.replace(' ', '_')}_Briefing.pdf",
    mime="application/pdf",
)
