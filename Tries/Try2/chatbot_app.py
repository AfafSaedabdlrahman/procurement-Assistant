import streamlit as st
import requests

# Backend API URL
API_URL = "http://127.0.0.1:8000/query/"

# Streamlit App Configuration
st.set_page_config(page_title="Procurement Data Query App", layout="wide")

# Initialize session state for messages if not already initialized
if 'messages' not in st.session_state:
    st.session_state.messages = []

# App Title and Instructions
st.title("AskBot  👋")
st.markdown("Greetings! I'm procurement assistant. Let's explore your data insights together!")
# User Input
user_query = st.text_input("Enter your query:", placeholder="E.g., 'What item name spent the most in 2013?'")

# Button to trigger query
if st.button("Submit Query"):
    if not user_query.strip():
        st.error("Please enter a valid query.")
    else:
        try:
            # Prepare the payload
            payload = {"user_query": user_query}
            
            # Show a loading spinner while waiting for the response
            with st.spinner('Processing your query...'):
                # Send the POST request to the backend
                response = requests.post(API_URL, json=payload)

            # Handle the response
            if response.status_code == 200:
                result = response.json()
                #st.success("Query executed successfully!")

                # Extract only the 'response' part and format it
                response_message = f"### Result:\n{result['response']}"

                # Store and display the formatted response
                st.session_state.messages.append({"role": "assistant", "message": response_message})
                with st.chat_message("assistant", avatar="🤖"):  # You can use your BOT_AVATAR here
                    st.markdown(response_message)
            else:
                st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
        except requests.exceptions.RequestException as e:
            st.error(f"Error communicating with the backend: {e}")
