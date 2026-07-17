import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI File Assistant", layout="wide")

# Sidebar
with st.sidebar:
    st.title("📁 Document Center")
    uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

    if uploaded_file:
        if st.button("Process Document"):
            with st.spinner("Analyzing..."):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), "application/pdf")}
                try:
                    res = requests.post(f"{API_URL}/upload", files=files)
                    st.success(res.json()["message"])
                except requests.exceptions.ConnectionError:
                    st.error("Backend Server is Offline! Run uvicorn first.")

    st.divider()
    if st.button("Clear Local Chat"):
        st.session_state.messages = []

# Chat UI
st.title("Chatbot Assistant")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask about your document..."):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    try:
        res = requests.post(f"{API_URL}/chat", json={"question": prompt})
        if res.status_code == 200:
            answer = res.json()["answer"]
            with st.chat_message("assistant"):
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
        else:
            st.error("Server Error: " + res.text)
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to Backend. Is Uvicorn running?")
