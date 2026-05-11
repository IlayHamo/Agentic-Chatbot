import os

import requests
from dotenv import load_dotenv

# Ensure .env is listed in .gitignore to prevent accidental API key exposure.
load_dotenv()

# --- Constants ---
BASE_URL = "https://server.iac.ac.il/api/v1/studentapi"
STATELESS_API_URL = f"{BASE_URL}/chat/completions"
AGENTIC_API_URL = f"{BASE_URL}/responses"

MAX_HISTORY_MESSAGES = 10
MAX_TOKENS = 10000
REQUEST_TIMEOUT = 180   # seconds


def _get_headers() -> dict[str, str]:
    api_key = os.getenv("API_KEY")
    if not api_key:
        raise RuntimeError("Missing API key. Add API_KEY to your .env file.")

    return {"Authorization": f"Bearer {api_key}"}


def _extract_output_text(data: dict) -> str:
    for item in data.get("output", []):
        if item.get("type") == "message":
            for content_block in item.get("content", []):
                if content_block.get("type") == "output_text":
                    return content_block.get("text", "")

    return ""


def classic_chat_completion(messages: list[dict]) -> str:
    # Truncate oldest messages to stay within token budget.
    if len(messages) > MAX_HISTORY_MESSAGES:
        messages = messages[-MAX_HISTORY_MESSAGES:]

    headers = _get_headers()

    payload = {
        "messages": messages,
        "max_completion_tokens": MAX_TOKENS,
    }

    response = requests.post(
        STATELESS_API_URL,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    # Project requirement: real-time token and quota tracking.
    quota_status = data.get("iac_quota_status")
    if quota_status:
        print(f"[Quota Status] {quota_status}")

    choices = data.get("choices", [])
    if choices:
        message = choices[0].get("message", {})
        content = message.get("content", "")
        if content:
            return content

    return "No response was returned by the API."


def agentic_chat_response(
    user_input: str | list[dict],
    instructions: str = "You are a helpful AI assistant.",
    reasoning_effort: str = "low",
    active_tools: list[str] | None = None,
) -> str:
    headers = _get_headers()

    # Normalise and deduplicate tool names before building the API payload.
    normalized_tools = []
    for tool_name in active_tools or []:
        if isinstance(tool_name, str):
            cleaned_tool = tool_name.strip()
            if cleaned_tool and cleaned_tool not in normalized_tools:
                normalized_tools.append(cleaned_tool)

    tools_list = [{"type": tool_name} for tool_name in normalized_tools]

    payload = {
        "input": user_input,
        "instructions": instructions,
        "reasoning": {"effort": reasoning_effort.lower()},
        "max_completion_tokens": MAX_TOKENS,
    }

    # Omit the key entirely rather than sending an empty list, which some API
    # endpoints reject.
    if tools_list:
        payload["tools"] = tools_list

    response = requests.post(
        AGENTIC_API_URL,
        headers=headers,
        json=payload,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    data = response.json()

    # Project requirement: real-time token and quota tracking.
    quota_status = data.get("iac_quota_status")
    if quota_status:
        print(f"[Quota Status] {quota_status}")

    response_text = _extract_output_text(data)
    if response_text:
        return response_text

    return "No response was returned by the API."
