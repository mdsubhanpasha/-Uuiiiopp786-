"""
Enterprise Intelligence Command Center Dashboard.

Streamlit Dashboard:
- Title: NAYEEM-ELDF Command Center
- st_autorefresh 10s
- Display head/tail/shape/dtypes/describe/sample
- Filters: isin/between/query widgets
- Charts: pivot_table, nlargest, groupby, rolling, crosstab
- KPIs: memory_usage/nunique/size
- Export buttons: csv/excel/parquet/json
"""

import os
import sys
import pandas as pd
import streamlit as st
import plotly.express as px

try:
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    def st_autorefresh(interval, key): pass

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.orchestration.enterprise_orchestration_pipeline_controller import run_master_enterprise_pipeline

st.set_page_config(
    page_title="NAYEEM-ELDF Command Center",
    page_icon="⚡",
    layout="wide"
)

# Auto refresh every 10 seconds
st_autorefresh(interval=10000, key="eldf_autorefresh")

st.title("⚡ NAYEEM-ELDF: Enterprise Live Data Fabric Command Center")
st.markdown("**Real-Time Data Intelligence, Feature Factory & Live Telemetry Stream**")

@st.cache_data(ttl=5)
def load_data():
    return run_master_enterprise_pipeline()

data = load_data()
telemetry_df = data["telemetry"]
mem_stats = data["memory_stats"]
quality = data["quality_metrics"]

# KPI Metrics Header
kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
with kpi_col1:
    st.metric("Total Live Records", len(telemetry_df))
with kpi_col2:
    st.metric("Unique Assets (nunique)", telemetry_df["asset_name"].nunique() if "asset_name" in telemetry_df.columns else telemetry_df.iloc[:, 0].nunique())
with kpi_col3:
    st.metric("Memory Footprint (bytes)", f"{mem_stats['optimized_memory_bytes']:,}")
with kpi_col4:
    st.metric("Memory Optimization", f"{mem_stats['optimization_percentage']:.1f}%")

st.divider()

# Tab Navigation
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Live Inspection & Profiling",
    "🔍 Intelligent Filtration & Query",
    "📈 Dimensional & Quantitative Analytics",
    "🏷️ NLP & Categorical Features",
    "📥 Export & Persistence"
])

with tab1:
    st.subheader("Data Profiling & Quality Assessment")
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.markdown("**df.shape:**")
        st.write(quality["shape"])
        st.markdown("**df.dtypes:**")
        st.write(quality["dtypes"])
    with sub_col2:
        st.markdown("**df.describe():**")
        st.dataframe(quality["describe"], use_container_width=True)

    st.markdown("**df.head():**")
    st.dataframe(telemetry_df.head(), use_container_width=True)

    st.markdown("**df.tail():**")
    st.dataframe(telemetry_df.tail(), use_container_width=True)

    st.markdown("**df.sample():**")
    st.dataframe(quality["sample"], use_container_width=True)

with tab2:
    st.subheader("Interactive Query & Filtering Engine")
    query_col1, query_col2 = st.columns(2)

    with query_col1:
        search_query = st.text_input("df.query() Expression:", value="pnl_estimate >= 0")
        try:
            query_filtered = telemetry_df.query(search_query)
            st.dataframe(query_filtered, use_container_width=True)
        except Exception as e:
            st.error(f"Query Error: {e}")

    with query_col2:
        if "unit_price" in telemetry_df.columns:
            min_val = float(telemetry_df["unit_price"].min())
            max_val = float(telemetry_df["unit_price"].max())
            selected_range = st.slider("Series.between() Price Filter:", min_val, max_val, (min_val, max_val))
            between_df = telemetry_df[telemetry_df["unit_price"].between(selected_range[0], selected_range[1])]
            st.dataframe(between_df, use_container_width=True)

with tab3:
    st.subheader("Pivot Heatmaps, Top Asset Rankings & Aggregations")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**df.nlargest() Top Gainers/Prices:**")
        val_col = "unit_price" if "unit_price" in telemetry_df.columns else telemetry_df.select_dtypes(include=["number"]).columns[0]
        top_df = telemetry_df.nlargest(5, columns=val_col)
        fig_top = px.bar(top_df, x="asset_name" if "asset_name" in top_df.columns else top_df.columns[0], y=val_col, title="Top Assets Ranking")
        st.plotly_chart(fig_top, use_container_width=True)

    with c2:
        st.markdown("**pd.crosstab() Contingency Matrix:**")
        crosstab_df = data["cubes"]["crosstab_matrix"]
        st.dataframe(crosstab_df, use_container_width=True)

with tab4:
    st.subheader("NLP Extraction & Categorical Binning")
    nlp_df = data["nlp"]["nlp_extracted"]
    st.dataframe(nlp_df, use_container_width=True)

with tab5:
    st.subheader("Persistence & Multi-Format Data Downloads")

    col_csv, col_json, col_parquet, col_excel = st.columns(4)

    with col_csv:
        csv_data = telemetry_df.to_csv(index=False).encode("utf-8")
        st.download_button("Download CSV (df.to_csv)", data=csv_data, file_name="master_telemetry.csv", mime="text/csv")

    with col_json:
        json_data = telemetry_df.to_json(orient="records")
        st.download_button("Download JSON (df.to_json)", data=json_data, file_name="master_telemetry.json", mime="application/json")

    with col_parquet:
        parquet_path = data["export_paths"]["parquet"]
        if os.path.exists(parquet_path):
            with open(parquet_path, "rb") as f:
                st.download_button("Download Parquet (df.to_parquet)", data=f.read(), file_name="master_telemetry_fabric.parquet")

    with col_excel:
        excel_path = data["export_paths"]["excel"]
        if os.path.exists(excel_path):
            with open(excel_path, "rb") as f:
                st.download_button("Download Excel Report (df.to_excel)", data=f.read(), file_name="enterprise_kpi_analytical_report.xlsx")
