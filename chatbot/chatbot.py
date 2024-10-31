import streamlit as st
import requests
import json
from typing import Dict
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Constants
# Fallback to default if not set
API_ENDPOINT = os.getenv('API_ENDPOINT', 'http://localhost:8000/estate/query')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))  # seconds


class ChatMessage:
    def __init__(self, text: str, is_user: bool):
        self.text = text
        self.is_user = is_user


def initialize_session_state():
    """Initialize session state variables if they don't exist."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'error' not in st.session_state:
        st.session_state.error = None


def send_query_to_backend(query: str) -> Dict:
    """
    Send query to backend API with retry mechanism.
    Returns the response dictionary or raises an exception.
    """
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "query": query
    }

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                API_ENDPOINT,
                headers=headers,
                data=json.dumps(data),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"Failed to connect to backend after {
                                MAX_RETRIES} attempts: {str(e)}")
            time.sleep(RETRY_DELAY)


def display_chat_messages():
    """Display all chat messages with appropriate styling."""
    for msg in st.session_state.messages:
        if msg.is_user:
            st.write(f"🧑 **You:** {msg.text}")
        else:
            st.write(f"🤖 **Assistant:** {msg.text}")


def display_error(error_message: str):
    """Display error message with appropriate styling."""
    st.error(f"Error: {error_message}")


def main():
    st.title("Chat Estate")
    st.write("Because finding your dream home shouldn't feel like pulling teeth—unless you're into that kind of thing.")

    # Initialize session state
    initialize_session_state()

    # Create chat input
    user_input = st.text_input("Type your message here:", key="user_input")

    # Handle user input
    if user_input:
        # Add user message to chat history
        st.session_state.messages.append(ChatMessage(user_input, True))

        try:
            # Send query to backend
            response = send_query_to_backend(user_input)

            if response.get("success"):
                # Add bot response to chat history
                st.session_state.messages.append(
                    ChatMessage(response["summary"], False)
                )
                st.session_state.error = None
            else:
                st.session_state.error = response.get(
                    "error", "Unknown error occurred")

        except Exception as e:
            st.session_state.error = str(e)

        # Clear input field (by changing key)
        st.text_input("Type your message here:", key="user_input_new")

    # Display chat history
    display_chat_messages()

    # Display error if any
    if st.session_state.error:
        display_error(st.session_state.error)

    # Add a simple footer
    st.markdown("---")
    st.markdown("*Powered by AI*")


if __name__ == "__main__":
    main()
