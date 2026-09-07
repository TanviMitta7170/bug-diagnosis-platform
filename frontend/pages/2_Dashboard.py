import streamlit as st
import requests
import plotly.express as px
import pandas as pd

API_BASE = "http://localhost:8001"
st.set_page_config(page_title="Dashboard", layout="wide")
st.title("Dashboard")
st.markdown("Overview of all bugs in the knowledge base.")
st.divider()

try:
    r    = requests.get(f"{API_BASE}/api/knowledge/bugs", timeout=5)
    bugs = r.json().get("bugs", [])
except:
    st.error("Cannot connect to API."); st.stop()

if not bugs:
    st.info("No bugs in knowledge base yet."); st.stop()

df = pd.DataFrame(bugs)

total    = len(df)
resolved = len(df[df["status"] == "Resolved"]) if "status" in df.columns else 0
open_ct  = total - resolved
res_rate = round((resolved / total) * 100, 1) if total > 0 else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Bugs", total)
col2.metric("Resolved", resolved)
col3.metric("Open", open_ct)
col4.metric("Resolution Rate", f"{res_rate}%")
st.divider()

col_a, col_b = st.columns(2)

if "severity" in df.columns:
    with col_a:
        st.subheader("Severity Breakdown")
        sev_counts = df["severity"].value_counts().reset_index()
        sev_counts.columns = ["Severity", "Count"]
        color_map = {"Critical": "#EF4444", "High": "#F97316", "Medium": "#EAB308", "Low": "#22C55E"}
        fig = px.pie(sev_counts, values="Count", names="Severity", color="Severity", color_discrete_map=color_map, hole=0.4)
        st.plotly_chart(fig, use_container_width=True)

if "component" in df.columns:
    with col_b:
        st.subheader("Bugs by Component")
        comp_counts = df["component"].value_counts().reset_index()
        comp_counts.columns = ["Component", "Count"]
        fig2 = px.bar(comp_counts, x="Component", y="Count", color="Count", color_continuous_scale="Blues")
        st.plotly_chart(fig2, use_container_width=True)

if "priority" in df.columns:
    st.subheader("Priority Distribution")
    pri_counts = df["priority"].value_counts().reset_index()
    pri_counts.columns = ["Priority", "Count"]
    fig3 = px.bar(pri_counts, x="Priority", y="Count", color="Priority",
                  color_discrete_map={"P1": "#EF4444", "P2": "#F97316", "P3": "#EAB308", "P4": "#22C55E"})
    st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.subheader("Recent Bugs")
display_cols = [c for c in ["id", "title", "severity", "priority", "component", "status"] if c in df.columns]
st.dataframe(df[display_cols].head(10), use_container_width=True)
