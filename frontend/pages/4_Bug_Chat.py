import streamlit as st
import requests

API_BASE = "http://localhost:8001"
st.set_page_config(page_title="Bug Chat", layout="wide")
st.title("Bug Chat")
st.markdown("Ask questions about bugs in plain English — answers are grounded in your knowledge base.")
st.divider()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption(f"Sources: {', '.join(msg['sources'])}")

if prompt := st.chat_input("Ask about a bug, root cause, or resolution..."):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            try:
                r       = requests.post(f"{API_BASE}/api/chat", json={"message": prompt}, timeout=120)
                data    = r.json()
                answer  = data.get("answer", "Could not find an answer.")
                sources = data.get("sources", [])
            except Exception as e:
                answer = f"Error: {e}"; sources = []
        st.markdown(answer)
        if sources:
            st.caption(f"Sources: {', '.join(sources)}")
    st.session_state.chat_history.append({"role": "assistant", "content": answer, "sources": sources})

if st.button("Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()