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
API_ENDPOINT = os.getenv('API_ENDPOINT', 'http://localhost:8000/query')
MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
RETRY_DELAY = int(os.getenv('RETRY_DELAY', '1'))

# Set Streamlit page config for dark theme
st.set_page_config(page_title="Chat Estate", page_icon="🤖")

# Custom CSS for dark theme and message alignment
st.markdown("""
    <style>
        /* General dark theme adjustments */
        .stApp {
            background-color: #1B1B1B;
            color: #FFFFFF;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Message container */
        .message-container {
            display: flex;
            flex-direction: column;
            gap: 1rem;
            padding: 1rem;
            margin-bottom: 2rem;
        }
        
        /* Message row */
        .message-row {
            display: flex;
            width: 100%;
            justify-content: flex-start;
            margin: 0.5rem 0;
        }
        
        .message-row.user {
            justify-content: flex-start;
        }
        
        /* Message bubble */
        .message-bubble {
            padding: 1rem;
            border-radius: 1rem;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        .user-message {
            background-color: #2E4D8F;
            color: white;
        }
        
        .bot-message {
            background-color: #2A2A2A;
            color: white;
        }
        
        /* Message content */
        .message-content {
            display: flex;
            align-items: flex-start;
            gap: 0.5rem;
        }
        
        .message-icon {
            flex-shrink: 0;
            margin-top: 0.2rem;
        }
        
        .message-text {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        
        /* Input styling */
        .stTextInput > div > div {
            background-color: #2A2A2A;
            color: white;
            border-color: #4A4A4A;
        }
        
        /* Title styling */
        h1 {
            text-align: center;
            padding: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)


class ChatMessage:
    def __init__(self, text: str, is_user: bool):
        self.text = text
        self.is_user = is_user


def initialize_session_state():
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'error' not in st.session_state:
        st.session_state.error = None


def send_query_to_backend(query: str) -> Dict:
    headers = {"Content-Type": "application/json"}
    data = {"query": query}

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                API_ENDPOINT,
                headers=headers,
                data=json.dumps(data),
                timeout=30
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if attempt == MAX_RETRIES - 1:
                raise Exception(f"Failed to connect to backend after {
                                MAX_RETRIES} attempts: {str(e)}")
            time.sleep(RETRY_DELAY)


def display_chat_messages():
    """Display chat messages with improved formatting."""
    st.markdown('<div class="message-container">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        message_type = "user-message" if msg.is_user else "bot-message"
        icon = "🧑" if msg.is_user else "🤖"
        alignment_class = "user" if msg.is_user else "bot"

        st.markdown(
            f'<div class="message-row {alignment_class}">'
            f'<div class="message-bubble {message_type}">'
            f'<div class="message-content">'
            f'<span class="message-icon">{icon}</span>'
            f'<div class="message-text">{msg.text}</div>'
            f'</div></div></div>',
            unsafe_allow_html=True
        )

    st.markdown('</div>', unsafe_allow_html=True)


def handle_user_input():
    """Process user input and update chat history."""
    if st.session_state.user_input and st.session_state.user_input.strip():
        user_message = st.session_state.user_input.strip()
        st.session_state.messages.append(ChatMessage(user_message, True))

        try:
            response = send_query_to_backend(user_message)

            if response.get("success"):
                st.session_state.messages.append(
                    ChatMessage(response["summary"], False)
                )
                st.session_state.error = None
            else:
                st.session_state.error = response.get(
                    "error", "Unknown error occurred")

        except Exception as e:
            st.session_state.error = str(e)

        # Clear the input
        st.session_state.user_input = ""


def main():
    st.title("Chat Estate")

    # Initialize session state
    initialize_session_state()

    # Create columns for better layout
    col1, col2, col3 = st.columns([1, 10, 1])

    with col2:
        # Display chat messages
        display_chat_messages()

        # Display error if any
        if st.session_state.error:
            st.error(f"Error: {st.session_state.error}")

        # Create chat input with callback
        st.text_input(
            "Type your message here:",
            key="user_input",
            on_change=handle_user_input,
            placeholder="Type your message and press Enter..."
        )


if __name__ == "__main__":
    main()
