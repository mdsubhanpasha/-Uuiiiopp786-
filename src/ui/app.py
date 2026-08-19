import streamlit as st
import requests
import os
import json
import pandas as pd
import io

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="TestGen AI - Enterprise QA",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Datadog-style dark theme
def load_custom_css():
    st.markdown("""
        <style>
        /* General dark theme styling - Datadog inspired */
        .stApp {
            background-color: #1E1E24;
            color: #DFDFE5;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
            font-weight: 600 !important;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background-color: #2A2A35;
            border-right: 1px solid #444;
        }

        /* Inputs and Textareas */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea,
        .stFileUploader {
            background-color: #2A2A35;
            color: #DFDFE5;
            border: 1px solid #555;
            border-radius: 4px;
        }

        /* Buttons */
        .stButton > button {
            background-color: #632CA6; /* Datadog purple-ish accent */
            color: #FFFFFF;
            border-radius: 4px;
            font-weight: 600;
            border: none;
            transition: background-color 0.2s ease;
        }
        .stButton > button:hover {
            background-color: #7B3EBF;
        }

        /* Dataframes / Tables */
        .stDataFrame {
            background-color: #2A2A35;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            color: #FFFFFF;
        }
        </style>
    """, unsafe_allow_html=True)

load_custom_css()

def main():
    st.sidebar.title("TestGen AI")
    st.sidebar.markdown("Enterprise QA Automation Tool")

    # Navigation
    st.sidebar.header("1. Ingestion")
    ingest_method = st.sidebar.radio("Source", ["GitHub URL", "Upload .zip"])

    st.sidebar.header("2. Configuration")
    gemini_key = st.sidebar.text_input("Gemini API Key", type="password")
    gh_token = st.sidebar.text_input("GitHub Token (Optional)", type="password")

    st.title("TestGen AI Dashboard")

    # Ingestion Form
    with st.container():
        st.subheader("Generate Tests")
        col1, col2 = st.columns([3, 1])

        uploaded_file = None
        github_url = None

        with col1:
            if ingest_method == "GitHub URL":
                github_url = st.text_input("Public GitHub Repository URL", placeholder="https://github.com/owner/repo")
            else:
                uploaded_file = st.file_uploader("Upload Codebase (.zip)", type=["zip"])

        with col2:
            st.write("") # spacing
            st.write("")
            generate_btn = st.button("Generate Test Suite", use_container_width=True)

    if generate_btn:
        if not gemini_key:
            st.error("Please provide a Gemini API Key in the sidebar.")
            return

        if ingest_method == "GitHub URL" and not github_url:
            st.error("Please provide a GitHub URL.")
            return

        if ingest_method == "Upload .zip" and not uploaded_file:
             st.error("Please upload a .zip file.")
             return

        with st.spinner("Analyzing codebase and generating 200+ test cases... (This may take a few minutes)"):
            try:
                # Prepare request
                files = None
                data = {
                    "gemini_key": gemini_key,
                    "github_token": gh_token if gh_token else ""
                }

                if ingest_method == "Upload .zip":
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/zip")}
                else:
                    data["github_url"] = github_url

                res = requests.post(f"{API_URL}/ingest_and_generate", data=data, files=files)

                if res.status_code == 200:
                    st.session_state["results"] = res.json()
                    st.success("Test suite generated successfully!")
                else:
                    st.error(f"Generation failed: {res.text}")
            except Exception as e:
                st.error(f"Failed to connect to API: {e}")

    # Display Results
    if "results" in st.session_state:
        data = st.session_state["results"]
        results = data.get("results", {})
        session_id = data.get("session_id")

        st.markdown("---")

        # Enterprise Metrics Dashboard
        col1, col2, col3 = st.columns(3)

        num_tests = len(results.get("test_cases", []))
        # Simulated metrics based on test count
        bugs_prevented = num_tests // 5
        time_saved = num_tests * 0.5 # Assume 30 mins per test saved

        with col1:
            st.metric(label="Total Tests Generated", value=num_tests)
        with col2:
            st.metric(label="Estimated Bugs Prevented", value=bugs_prevented)
        with col3:
            st.metric(label="Time Saved (Hours)", value=f"{time_saved:.1f}")

        st.markdown("---")

        # Main content area
        col_chart, col_table = st.columns([1, 2])

        with col_chart:
            st.subheader("Predicted Coverage")
            coverage = results.get("predicted_coverage_percent", 0)

            # Simple donut chart using matplotlib (or just a large metric if preferred)
            # For Streamlit without extra plotting deps, we can use a progress bar or metric
            st.markdown(f"<h1 style='text-align: center; color: #10B981; font-size: 4rem;'>{coverage}%</h1>", unsafe_allow_html=True)
            st.progress(coverage / 100.0)
            st.caption("Based on generated test suite analysis")

        with col_table:
            st.subheader("Test Cases")
            test_cases = results.get("test_cases", [])
            if test_cases:
                df = pd.DataFrame(test_cases)
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.info("No test cases generated.")

        # Export Section
        st.markdown("---")
        st.subheader("Export Options")

        col_ex1, col_ex2, col_ex3 = st.columns(3)

        with col_ex1:
            if test_cases:
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Cases (CSV)",
                    data=csv,
                    file_name='test_cases.csv',
                    mime='text/csv',
                    use_container_width=True
                )

        with col_ex2:
             try:
                 res = requests.get(f"{API_URL}/export/scripts/{session_id}")
                 if res.status_code == 200:
                     st.download_button(
                         label="Download Scripts (.zip)",
                         data=res.content,
                         file_name="generated_tests.zip",
                         mime="application/x-zip-compressed",
                         use_container_width=True
                     )
             except Exception as e:
                 st.error(f"Failed to fetch scripts export: {e}")

        with col_ex3:
             if st.button("Export to Jira/TestRail (JSON)", use_container_width=True):
                 try:
                     res = requests.get(f"{API_URL}/export/jira/{session_id}")
                     if res.status_code == 200:
                         json_data = json.dumps(res.json(), indent=2)
                         st.download_button(
                             label="Save JSON",
                             data=json_data,
                             file_name="jira_export.json",
                             mime="application/json"
                         )
                 except Exception as e:
                     st.error(f"Failed to fetch export: {e}")

if __name__ == "__main__":
    main()
