import streamlit as st
import requests

API_BASE = "http://localhost:8001"

st.set_page_config(page_title="Bug Diagnosis Platform", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("Bug Diagnosis Platform")
st.sidebar.markdown("*Intelligent multi-agent bug diagnosis*")
st.sidebar.divider()

try:
    r = requests.get(f"{API_BASE}/health", timeout=3)
    if r.status_code == 200:
        data = r.json()
        st.sidebar.success("API Connected")
        st.sidebar.metric("Bugs in Knowledge Base", data.get("bugs_in_kb", 0))
    else:
        st.sidebar.error("API not responding")
except:
    st.sidebar.warning("API offline — start backend first")

st.sidebar.divider()
st.sidebar.page_link("pages/1_Bug_Analyzer.py",  label="Bug Analyzer")
st.sidebar.page_link("pages/2_Dashboard.py",      label="Dashboard")
st.sidebar.page_link("pages/3_Bug_Prediction.py", label="Bug Prediction")
st.sidebar.page_link("pages/4_Bug_Chat.py",       label="Bug Chat")
st.sidebar.page_link("pages/5_Knowledge_Base.py", label="Knowledge Base")
st.sidebar.page_link("pages/6_Bug_History.py",    label="Bug History")

st.title("Creation of Intelligent Bug Diagnosis Platform")
st.markdown("#### with Fix Recommendation Assistance")
st.divider()

col1, col2, col3 = st.columns(3)
col1.info("**Bug Analyzer**\n\nSubmit a bug report — 5 agents analyze it and deliver structured fix guidance.")
col2.success("**Dashboard**\n\nKPI metrics, severity distribution, component and priority charts.")
col3.warning("**Bug Prediction**\n\nAnalyze a git commit diff to flag high-risk changes before production.")

col4, col5, col6 = st.columns(3)
col4.info("**Bug Chat**\n\nAsk questions about past bugs grounded in the knowledge base.")
col5.success("**Knowledge Base**\n\nSearch, filter, view, and add resolved bugs.")
col6.warning("**Bug History**\n\nAll past analyses with resolution tracking and search.")

st.divider()
st.markdown("### Agent Pipeline")
agents = [("1. Triage","Severity and priority"),("2. Log Analysis","Parse stack trace"),("3. Duplicate Detection","Find similar bugs"),("4. Root Cause","Probable cause"),("5. Remediation","Fix recommendation")]
cols = st.columns(5)
for col, (name, desc) in zip(cols, agents):
    with col:
        st.markdown(f"**{name}**")
        st.caption(desc)
