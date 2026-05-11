import requests
import streamlit as st

from backend import agentic_chat_response, classic_chat_completion

STATELESS_MODE = "Stateless (Fast)"
AGENTIC_MODE = "Agentic (Web Search)"
DEFAULT_INSTRUCTIONS = "You are a helpful AI assistant."


def get_active_chat_key(selected_mode: str) -> str:
    return "stateless_messages" if selected_mode == STATELESS_MODE else "agentic_messages"


def get_greeting(selected_mode: str) -> str:
    if selected_mode == STATELESS_MODE:
        return "Hi! I'm the fast stateless assistant. I maintain conversation history for context. How can I help?"

    return "Hello! I'm your agentic assistant. I can search the web for real-time information. What would you like to know?"


def show_user_friendly_error(error: Exception) -> None:
    if isinstance(error, requests.exceptions.ConnectionError):
        st.error("🌐 Connection Error: Please check your internet connection and try again.")
        return

    if isinstance(error, requests.exceptions.Timeout):
        st.error("⏱️ Timeout Error: The server took too long to respond. Please try again.")
        return

    if isinstance(error, requests.exceptions.HTTPError):
        status_code = error.response.status_code if error.response is not None else None
        if status_code == 401:
            st.error("🔑 Authentication Error: Your API key is invalid, expired, or missing. Please check your .env file.")
        elif status_code == 429:
            st.error("⚠️ Rate Limit Error: You've made too many requests. Please wait a moment and try again.")
        elif status_code is not None and status_code >= 500:
            st.error("🔧 Server Error: The AI service is temporarily unavailable. Please try again later.")
        else:
            st.error(f"❌ Request Error: {error}")
        return

    st.error(f"❌ An unexpected error occurred: {error}")


st.set_page_config(page_title="IAC Smart AI Agent", page_icon="💬", layout="centered")
st.title("IAC Smart AI Agent")
st.caption("Choose your mode: Stateless for quick responses, Agentic for web search capabilities.")

# Two separate histories prevent mode-switching from corrupting either conversation.
st.session_state.setdefault("stateless_messages", [])
st.session_state.setdefault("agentic_messages", [])

with st.sidebar:
    st.header("Settings")

    mode = st.radio(
        "Select Model Mode:",
        options=[STATELESS_MODE, AGENTIC_MODE],
        index=0,
    )

    if mode == STATELESS_MODE:
        st.caption("⚡ Fast, stateless responses based on conversation history. No web search.")
    else:
        st.caption("🔍 Agentic mode with real-time web search capabilities. One-shot responses.")

    # Defaults defined here so these variables are always in scope regardless of mode.
    system_instructions = DEFAULT_INSTRUCTIONS
    reasoning_effort = "low"
    active_tools = ["web_search"]
    if mode == AGENTIC_MODE:
        system_instructions = st.text_input(
            "System Instructions:",
            value=DEFAULT_INSTRUCTIONS,
            help="Instructions for the AI agent to follow."
        )
        reasoning_effort = st.selectbox(
            "Reasoning Effort:",
            options=["low", "medium", "high"],
            index=0,
            format_func=str.title,
            help="Choose the reasoning effort level for the AI agent."
        )

    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state[get_active_chat_key(mode)] = []
        st.rerun()

active_chat_key = get_active_chat_key(mode)
active_messages = st.session_state[active_chat_key]

if not active_messages:
    active_messages.append({"role": "assistant", "content": get_greeting(mode)})

for msg in active_messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_prompt = st.chat_input("Type your message...")

if user_prompt:
    active_messages.append({"role": "user", "content": user_prompt})

    with st.chat_message("user"):
        st.markdown(user_prompt)

    spinner_text = "Generating fast response..." if mode == STATELESS_MODE else "Scanning the web..."

    with st.spinner(spinner_text):
        try:
            if mode == STATELESS_MODE:
                response = classic_chat_completion(active_messages)
            else:
                response = agentic_chat_response(
                    active_messages,
                    instructions=system_instructions,
                    reasoning_effort=reasoning_effort,
                    active_tools=active_tools,
                )

            active_messages.append({"role": "assistant", "content": response})

            with st.chat_message("assistant"):
                st.markdown(response)

        except Exception as e:
            # Roll back the optimistically appended user message on failure.
            active_messages.pop()
            show_user_friendly_error(e)
