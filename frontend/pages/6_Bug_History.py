import streamlit as st
import requests

API_BASE = "http://localhost:8001"
st.set_page_config(page_title="Bug History", layout="wide")
st.title("Bug History")
st.markdown("All previously analyzed bugs — search, filter, resolve, or delete.")
st.divider()

try:
    r       = requests.get(f"{API_BASE}/api/history/all", timeout=5)
    history = r.json().get("history", [])
except:
    st.error("Cannot connect to API."); st.stop()

if not history:
    st.info("No analyses yet. Submit a bug in the Bug Analyzer to get started.")
    st.stop()

col1, col2, col3 = st.columns(3)
search   = col1.text_input("Search", placeholder="Search logs or component...")
f_sev    = col2.selectbox("Filter by Severity", ["All", "Critical", "High", "Medium", "Low"])
f_status = col3.selectbox("Filter by Status", ["All", "Open", "Resolved"])

filtered = history
if search:
    filtered = [h for h in filtered if search.lower() in h.get("log_snippet", "").lower() or search.lower() in h.get("component", "").lower()]
if f_sev != "All":
    filtered = [h for h in filtered if h.get("severity") == f_sev]
if f_status != "All":
    filtered = [h for h in filtered if h.get("status") == f_status]

st.caption(f"Showing {len(filtered)} of {len(history)} analyses")
st.divider()

for entry in filtered:
    sev    = entry.get("severity", "—")
    status = entry.get("status", "Open")
    with st.expander(f"**{entry.get('id', '—')}** | {sev} | {entry.get('component', '—')} | {entry.get('timestamp', '—')} | {status}"):
        st.markdown("**Log Snippet:**")
        st.code(entry.get("log_snippet", "—"), language="text")
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Severity:** {sev}")
        col2.markdown(f"**Priority:** {entry.get('priority', '—')}")
        col3.markdown(f"**Environment:** {entry.get('environment', '—')}")

        if status == "Resolved":
            st.success(f"Resolved at {entry.get('resolved_at', '—')}")
            st.markdown(f"**Applied Fix:** {entry.get('applied_fix', '—')}")
            st.markdown(f"**Resolution Notes:** {entry.get('resolution_notes', '—')}")
        else:
            st.divider()
            st.markdown("**Mark as Resolved:**")
            with st.form(f"resolve_{entry.get('id')}"):
                applied_fix = st.text_input("Applied Fix", placeholder="What fix was applied?")
                notes       = st.text_area("Resolution Notes", placeholder="Any additional notes...", height=80)
                col_r, col_d = st.columns(2)
                resolve_btn  = col_r.form_submit_button("Mark Resolved", type="primary")
                delete_btn   = col_d.form_submit_button("Delete")

                if resolve_btn:
                    try:
                        requests.put(f"{API_BASE}/api/history/resolve/{entry.get('id')}", json={"notes": notes, "applied_fix": applied_fix}, timeout=5)
                        st.success("Marked as resolved.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

                if delete_btn:
                    try:
                        requests.delete(f"{API_BASE}/api/history/{entry.get('id')}", timeout=5)
                        st.success("Deleted.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")

        if entry.get("results"):
            with st.expander("View Full Analysis Results"):
                st.json(entry.get("results"))
