# # import streamlit as st
 
# # # Set page configuration
# # st.set_page_config(page_title="AI File Assistant", layout="wide")
 
# # # --- SIDEBAR: File Upload ---
# # with st.sidebar:
# #     st.title("📁 Document Center")
# #     uploaded_files = st.file_uploader(
# #         "Upload your files here",
# #         accept_multiple_files=True,
# #         type=['pdf', 'txt', 'csv', 'docx']
# #     )
   
# #     if uploaded_files:
# #         st.success(f"{len(uploaded_files)} file(s) uploaded successfully!")
# #         for file in uploaded_files:
# #             st.write(f"• {file.name}")
   
# #     st.divider()
# #     if st.button("Clear Chat History"):
# #         st.session_state.messages = []
# #         st.rerun()
 
# # # --- MAIN INTERFACE: Chatbot ---
# # st.title("💬 Chatbot Assistant")
 
# # # Initialize chat history
# # if "messages" not in st.session_state:
# #     st.session_state.messages = []
 
# # # Display chat messages from history on app rerun
# # for message in st.session_state.messages:
# #     with st.chat_message(message["role"]):
# #         st.markdown(message["content"])
 
# # # React to user input
# # if prompt := st.chat_input("How can I help you?"):
# #     # Display user message in chat message container
# #     st.chat_message("user").markdown(prompt)
   
# #     # Add user message to chat history
# #     st.session_state.messages.append({"role": "user", "content": prompt})
 
# #     # Placeholder for actual AI logic (e.g., OpenAI or Anthropic)
# #     response = f"I see you said: '{prompt}'. "
# #     if uploaded_files:
# #         response += f"I have access to {len(uploaded_files)} files in the sidebar."
# #     else:
# #         response += "I don't see any files uploaded yet."
 
# #     # Display assistant response
# #     with st.chat_message("assistant"):
# #         st.markdown(response)
   
# #     # Add assistant response to historyt
# #     st.session_state.messages.append({"role": "assistant", "content": response})



# import streamlit as st
# import requests

# # API_URL = "http://localhost:8000"
# # API_URL = "http://localhost:8000"
# API_URL = "http://127.0.0.1:8000"

# st.set_page_config(page_title="AI File Assistant", layout="wide")

# # Sidebar
# with st.sidebar:
#     st.title("📁 Document Center")
#     uploaded_file = st.file_uploader("Upload PDF", type=["pdf"])

#     if uploaded_file:
#         files = {"file": uploaded_file}
#         res = requests.post(f"{API_URL}/upload", files=files)
#         st.success(res.json()["message"])

#     if st.button("Show Chat History"):
#         res = requests.get(f"{API_URL}/history")
#         history = res.json()["history"]
#         for role, msg in history:
#             st.write(f"**{role}**: {msg}")

# # Chat UI
# st.title("💬 Chatbot Assistant")

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# for msg in st.session_state.messages:
#     with st.chat_message(msg["role"]):
#         st.markdown(msg["content"])

# if prompt := st.chat_input("Ask something..."):
#     st.chat_message("user").markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     res = requests.post(
#         f"{API_URL}/chat",
#         json={"question": prompt}
#     )

#     answer = res.json()["answer"]

#     with st.chat_message("assistant"):
#         st.markdown(answer)

#     st.session_state.messages.append({"role": "assistant", "content": answer})


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