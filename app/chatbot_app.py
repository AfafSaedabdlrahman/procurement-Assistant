import json
import pandas as pd
import streamlit as st
import requests

st.title("BuyBot at your service👋")
st.write("Greetings! I'm your procurement assistant.\nTogether, we can get any procurement information you want.")

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
        # st.error(f"Error loading chat history: {e}")

# Sidebar with a button to delete chat history
with st.sidebar:
    if st.button("Delete Chat History"):
        st.session_state.messages = []
        try:
            requests.delete(f"{BACKEND_URL}/api/v1/chat/history/{session_name}")
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
    st.session_state.messages.append({"role": "user", "message": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.markdown(prompt)

    headers = {'Content-Type': 'application/json'}
    payload = json.dumps({"request": prompt})

    with st.spinner("Generating response..."):
        try:
            res = requests.post(f"{BACKEND_URL}/api/v1/chat/submit/{session_name}",
                                data=payload,
                                headers=headers)
            res.raise_for_status()
            response_json = res.json()

            # Display processed data from /process-data endpoint as a table
            data = response_json.get("data", [])
            if data:
                #st.subheader("Processed Data:")
                # Convert data to DataFrame
                df = pd.DataFrame(data)
                # Display the table
                st.table(df)
            else:
                st.write("No data available to display.")

            # Get the assistant's response message
            response_message = response_json.get("message", None)
            if response_message:  # Only display the message and avatar if there's a valid response
                st.session_state.messages.append({"role": "assistant", "message": response_message})
                with st.chat_message("assistant", avatar=BOT_AVATAR):
                    st.markdown(response_message)

        except requests.exceptions.RequestException as e:
            st.error(f"Error sending message: {e}")

    # Save chat history after each interaction
    try:
        requests.post(f"{BACKEND_URL}/api/v1/chat/history/{session_name}", json=st.session_state.messages)
    except requests.exceptions.RequestException as e:
        st.error(f"Error saving chat history: {e}")
