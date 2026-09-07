import streamlit as st
import requests

API_BASE = "http://localhost:8001"
st.set_page_config(page_title="Bug Prediction", layout="wide")
st.title("Bug Prediction")
st.markdown("Paste a git commit diff to predict bug risk before the change reaches production.")
st.divider()

commit_msg  = st.text_input("Commit Message", placeholder="e.g. Fix null check in UserService")
author      = st.text_input("Author", placeholder="e.g. developer@company.com")
commit_diff = st.text_area("Git Commit Diff", placeholder="Paste your git diff here...", height=300)

run_btn = st.button("Analyze Commit Risk", type="primary", use_container_width=True)
st.divider()

if run_btn:
    if not commit_diff or len(commit_diff.strip()) < 10:
        st.error("Please paste a git commit diff."); st.stop()
    try:
        requests.get(f"{API_BASE}/health", timeout=3)
    except:
        st.error("Backend not running."); st.stop()

    with st.spinner("Analyzing commit risk..."):
        try:
            r    = requests.post(f"{API_BASE}/api/predict", json={"commit_diff": commit_diff, "commit_message": commit_msg, "author": author}, timeout=60)
            data = r.json().get("result", {})
        except Exception as e:
            st.error(f"Error: {e}"); st.stop()

    risk  = data.get("risk_level", "—")
    score = data.get("risk_score", 0)
    st.markdown(f"### Risk Level: **{risk}** ({score}/100)")
    st.progress(score / 100)
    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Risk Reasons")
        for r in data.get("risk_reasons", []): st.markdown(f"- {r}")
        st.subheader("Vulnerable Areas")
        for a in data.get("vulnerable_areas", []): st.markdown(f"- {a}")
    with col2:
        st.subheader("Recommended Tests")
        for t in data.get("recommended_tests", []): st.markdown(f"- {t}")

    st.divider()
    st.markdown(f"**Summary:** {data.get('summary', '—')}")
