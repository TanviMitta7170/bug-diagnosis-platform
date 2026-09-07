import streamlit as st
import requests

API_BASE = "http://localhost:8001"
st.set_page_config(page_title="Knowledge Base", layout="wide")
st.title("Knowledge Base")
st.markdown("Search, filter, view, and add resolved bugs.")
st.divider()

try:
    r     = requests.get(f"{API_BASE}/api/knowledge/count", timeout=3)
    count = r.json().get("count", 0)
    st.metric("Total Bugs Indexed", count)
except:
    st.error("Cannot connect to API."); st.stop()

st.divider()

col1, col2, col3 = st.columns(3)
search   = col1.text_input("Search", placeholder="Search title or description...")
f_sev    = col2.selectbox("Filter by Severity", ["All", "Critical", "High", "Medium", "Low"])
f_comp   = col3.selectbox("Filter by Component", ["All", "Auth/OAuth", "Database Layer", "API Gateway", "Frontend/UI", "Scheduler/Jobs", "Other"])

st.divider()
st.subheader("Indexed Bugs")

try:
    r    = requests.get(f"{API_BASE}/api/knowledge/bugs", timeout=5)
    bugs = r.json().get("bugs", [])
except Exception as e:
    st.error(f"Failed to load bugs: {e}"); bugs = []

filtered = bugs
if search:
    filtered = [b for b in filtered if search.lower() in b.get("title", "").lower() or search.lower() in b.get("stack_trace", "").lower()]
if f_sev != "All":
    filtered = [b for b in filtered if b.get("severity") == f_sev]
if f_comp != "All":
    filtered = [b for b in filtered if b.get("component") == f_comp]

st.caption(f"Showing {len(filtered)} of {len(bugs)} bugs")

if not filtered:
    st.info("No bugs match your filters.")
else:
    for bug in filtered:
        sev    = bug.get("severity", "—")
        status = bug.get("status", "Open")
        with st.expander(f"**{bug.get('id', '—')}** — {bug.get('title', 'Untitled')} [{sev}] [{status}]"):
            col1, col2, col3 = st.columns(3)
            col1.markdown(f"**Severity:** {sev}")
            col2.markdown(f"**Priority:** {bug.get('priority', '—')}")
            col3.markdown(f"**Component:** {bug.get('component', '—')}")
            st.markdown(f"**Root Cause:** {bug.get('root_cause', '—')}")
            st.markdown(f"**Resolution:** {bug.get('resolution', '—')}")
            if bug.get("stack_trace"):
                st.code(bug.get("stack_trace"), language="text")

st.divider()
st.subheader("Add Resolved Bug")

with st.form("add_bug_form"):
    col1, col2   = st.columns(2)
    bug_id       = col1.text_input("Bug ID", placeholder="BUG-011")
    title        = col2.text_input("Title")
    stack_trace  = st.text_area("Stack Trace", height=100)
    root_cause   = st.text_area("Root Cause", height=80)
    resolution   = st.text_area("Resolution", height=80)
    col3, col4, col5 = st.columns(3)
    severity  = col3.selectbox("Severity", ["Critical", "High", "Medium", "Low"])
    priority  = col4.selectbox("Priority", ["P1", "P2", "P3", "P4"])
    component = col5.selectbox("Component", ["Auth/OAuth", "Database Layer", "API Gateway", "Frontend/UI", "Scheduler/Jobs", "Other"])

    if st.form_submit_button("Add to Knowledge Base", type="primary"):
        if not all([bug_id, title, stack_trace, root_cause, resolution]):
            st.error("Please fill in all fields.")
        else:
            payload = {"id": bug_id, "title": title, "stack_trace": stack_trace, "root_cause": root_cause,
                       "resolution": resolution, "severity": severity, "priority": priority, "component": component, "status": "Resolved"}
            try:
                r = requests.post(f"{API_BASE}/api/knowledge/add", json=payload, timeout=10)
                if r.status_code == 200:
                    st.success(r.json()["message"])
                    st.rerun()
                else:
                    st.error(f"Error: {r.text}")
            except Exception as e:
                st.error(f"Failed: {e}")
