import streamlit as st
import requests

API_BASE = "http://localhost:8001"
st.set_page_config(page_title="Bug Analyzer", layout="wide")

SAMPLE_CASES = {
    "Select a sample...": ("", ""),
    "NullPointerException (Java)": (
        "Auth/OAuth",
        "NullPointerException at UserService.java:142\n  at com.app.service.UserService.getProfile(UserService.java:142)\n  at com.app.controller.UserController.fetchUser(UserController.java:67)\nCaused by: java.lang.NullPointerException\n  -- user.getAccountId() returned null after OAuth token refresh"
    ),
    "Database Connection Timeout": (
        "Database Layer",
        "TimeoutException: Unable to acquire connection from pool after 30000ms\n  at com.zaxxer.hikari.pool.HikariPool.getConnection(HikariPool.java:213)\n  at org.springframework.jdbc.datasource.DataSourceUtils.getConnection\nCaused by: Connection pool exhausted — max-size=10, all connections in use"
    ),
    "Python KeyError": (
        "API Gateway",
        "Traceback (most recent call last):\n  File \"app/api/routes.py\", line 89, in process_request\n    user_id = request_data['user']['id']\nKeyError: 'user'\n  -- request_data dict missing 'user' key on unauthenticated requests"
    ),
    "React TypeError": (
        "Frontend/UI",
        "TypeError: Cannot read properties of null (reading 'displayName')\n    at UserProfile (UserProfile.jsx:34)\n    at renderWithHooks (react-dom.development.js:14985)\n  -- user object is null after logout, Redux store not cleared"
    ),
}

def render_result(key, result):
    if key == "triage":
        sev = result.get("severity", "—")
        pri = result.get("priority", "—")
        conf = result.get("confidence", None)
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Severity:** {sev}")
        col1.markdown(f"**Priority:** {pri}")
        col2.markdown(f"**Component:** {result.get('affected_component','—')}")
        col2.markdown(f"**Affected Users:** {result.get('affected_users','—')}")
        if conf is not None:
            col3.markdown(f"**Confidence:** {conf}%")
            col3.progress(int(conf) / 100)
        st.markdown(f"**Reasoning:** {result.get('reasoning','—')}")
    elif key == "log_analysis":
        st.markdown(f"**Exception:** `{result.get('exception_type','—')}`")
        st.markdown(f"**Failure Point:** `{result.get('failure_point','—')}`")
        chain = result.get("call_chain", [])
        if chain:
            st.code(" -> ".join(str(c) for c in chain), language="text")
        st.markdown(f"**Diagnostic Signal:** {result.get('diagnostic_signal','—')}")
    elif key == "duplicates":
        matches = result.get("matches", [])
        if matches:
            for m in matches:
                score = m.get("similarity_score", 0)
                st.markdown(f"**{m.get('bug_id','—')}** — {m.get('title','—')} ({score}% similar)")
                st.caption(f"Why similar: {m.get('similarity_reason','—')}")
                st.caption(f"Resolution: {m.get('resolution','—')}")
                st.divider()
        else:
            st.info("No similar bugs found.")
        st.markdown(f"**Recommendation:** {result.get('recommendation','—')}")
    elif key == "root_cause":
        conf = result.get("confidence", "—")
        score = result.get("confidence_score", None)
        st.markdown(f"**Primary Cause:** {result.get('primary_cause','—')}")
        col1, col2 = st.columns(2)
        col1.markdown(f"**Confidence:** {conf}")
        if score is not None:
            col2.progress(int(score) / 100)
            col2.caption(f"{score}%")
        st.markdown(f"**Supporting Evidence:** {result.get('supporting_evidence','—')}")
        st.markdown(f"**Affected Subsystem:** {result.get('affected_subsystem','—')}")
        if result.get("secondary_hypothesis"):
            st.caption(f"Alternative hypothesis: {result.get('secondary_hypothesis')}")
    elif key == "remediation":
        st.markdown(f"**Fix Approach:** {result.get('fix_approach','—')}")
        for step in result.get("fix_steps", []):
            st.markdown(f"- {step}")
        col1, col2 = st.columns(2)
        col1.markdown(f"**Confidence:** {result.get('confidence','—')}")
        col1.markdown(f"**Estimated Effort:** {result.get('estimated_effort','—')}")
        col2.markdown(f"**Reviewer:** {result.get('reviewer_suggestion','—')}")
        col2.markdown(f"**Grounded in History:** {'Yes' if result.get('grounded_in_history') else 'No'}")
        if result.get("prevention_tip"):
            st.info(f"Prevention tip: {result.get('prevention_tip')}")

st.title("Bug Analyzer")
st.markdown("Submit a bug report and watch all 5 agents analyze it.")
st.divider()

sample = st.selectbox("Load a sample case", list(SAMPLE_CASES.keys()))
sample_component, sample_log = SAMPLE_CASES[sample] if sample != "Select a sample..." else ("", "")

col1, col2 = st.columns([2, 1])
with col1:
    log_input = st.text_area("Stack Trace / Error Log", value=sample_log, placeholder="Paste your stack trace or error log...", height=220)
with col2:
    component_options = ["Auth/OAuth", "Database Layer", "API Gateway", "Frontend/UI", "Scheduler/Jobs", "Other"]
    default_idx = component_options.index(sample_component) if sample_component in component_options else 0
    component   = st.selectbox("Affected Component", component_options, index=default_idx)
    environment = st.selectbox("Environment", ["Production", "Staging", "Development", "QA"])
    file_upload = st.file_uploader("Upload a log file (.txt/.log)", type=["txt", "log"])
    if file_upload:
        log_input = file_upload.read().decode("utf-8")
        st.success(f"Loaded: {file_upload.name}")

col_run, col_clear = st.columns([3, 1])
run_btn   = col_run.button("Analyze with Agents", type="primary", use_container_width=True)
clear_btn = col_clear.button("Clear", use_container_width=True)
if clear_btn:
    st.rerun()

st.divider()

AGENTS = [
    ("1. Triage", "triage"),
    ("2. Log Analysis", "log_analysis"),
    ("3. Duplicates", "duplicates"),
    ("4. Root Cause", "root_cause"),
    ("5. Remediation", "remediation"),
]

if run_btn:
    if not log_input or len(log_input.strip()) < 10:
        st.error("Please enter a bug report."); st.stop()
    try:
        requests.get(f"{API_BASE}/health", timeout=3)
    except:
        st.error("Backend not running. Start with: uvicorn main:app --reload"); st.stop()

    st.markdown("### Agent Pipeline")
    pcols = st.columns(5)
    phs = []
    for i, (name, _) in enumerate(AGENTS):
        with pcols[i]:
            ph = st.empty()
            ph.info(name)
            phs.append(ph)
    st.divider()

    with st.spinner("Running agent pipeline..."):
        try:
            r    = requests.post(f"{API_BASE}/api/analyze", json={"log": log_input, "component": component, "environment": environment}, timeout=90)
            data = r.json()
        except requests.exceptions.Timeout:
            st.error("Request timed out. Try again."); st.stop()
        except Exception as e:
            st.error(f"API error: {e}"); st.stop()

    results = data.get("results", {})
    errors  = data.get("errors") or {}

    for i, (name, key) in enumerate(AGENTS):
        result    = results.get(key, {})
        has_error = "error" in result
        if has_error:
            phs[i].error(name)
        else:
            phs[i].success(name)
        with st.expander(f"**{name}** — {'Complete' if not has_error else 'Error'}", expanded=True):
            if has_error:
                st.error(result.get("error", "Unknown error"))
            else:
                render_result(key, result)

    triage = results.get("triage", {})
    try:
        requests.post(f"{API_BASE}/api/history/add", json={
            "log_snippet": log_input[:200],
            "component":   component,
            "environment": environment,
            "severity":    triage.get("severity", "Unknown"),
            "priority":    triage.get("priority", "Unknown"),
            "confidence":  triage.get("confidence", None),
            "status":      "Open",
            "results":     results
        }, timeout=5)
    except:
        pass

    if not errors:
        st.success("All 5 agents completed successfully.")
