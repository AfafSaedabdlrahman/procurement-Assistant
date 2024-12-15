import json
import streamlit as st
import requests

st.title("Welcome to procurement Chatbot! 👋")
st.write("Greetings! I'm your churn assistant. Let's explore your data insights together!")

USER_AVATAR = "👤"
BOT_AVATAR = "🤖"
BACKEND_URL = "http://localhost:8000"

# Initialize or load chat history
session_name = "default"
if "messages" not in st.session_state:
    try:
        response = requests.get(f"{BACKEND_URL}/api/v1/chat/history/{session_name}")
        response.raise_for_status()
        st.session_state.messages = response.json()
    except requests.exceptions.RequestException as e:
        st.session_state.messages = []
        st.error(f"Error loading chat history: {e}")

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        try:
            res = requests.delete(f"{BACKEND_URL}/api/v1/chat/history/{session_name}")
            res.raise_for_status()
            st.success("Chat history deleted successfully!")
        except requests.exceptions.RequestException as e:
            st.error(f"Error deleting chat history: {e}")

# Display chat messages
for message in st.session_state.messages:
    avatar = USER_AVATAR if message["role"] == "user" else BOT_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["message"])

# Main chat interface
prompt = st.chat_input("How can I help?")
if prompt:
    # Add user's query to chat history
    st.session_state.messages.append({"role": "user", "message": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"user_query": prompt})  # Match the FastAPI input model

    with st.spinner("Generating response..."):
        try:
            res = requests.post(f"{BACKEND_URL}/query", data=payload, headers=headers)
            res.raise_for_status()
            response_json = res.json()
            pandas_command = response_json.get("pandas_command", "No command found")
            result = response_json.get("result", "No result found")

            # Format assistant response
            response_message = f"### Command:\n```\n{pandas_command}\n```\n### Result:\n{result}"
            st.session_state.messages.append({"role": "assistant", "message": response_message})
            with st.chat_message("assistant", avatar=BOT_AVATAR):
                st.markdown(response_message)
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with the backend: {e}")

    # Save chat history after each interaction
    try:
        res = requests.post(f"{BACKEND_URL}/api/v1/chat/history/{session_name}", json=st.session_state.messages)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving chat history: {e}")
