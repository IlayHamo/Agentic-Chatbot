# IAC Smart AI Agent

A Streamlit-based chat application that connects to the IAC GPT-5-NANO model. Supports two operating modes: a fast stateless chat and an agentic mode with real-time web search.

---

## Features

- **Stateless (Fast) mode** — sends full conversation history with every request for multi-turn context, with automatic truncation to keep token usage in check.
- **Agentic (Web Search) mode** — single-turn requests with web search tool support and configurable reasoning effort.
- Separate, independent chat histories per mode — switching modes never loses a conversation.
- User-friendly error handling for network, authentication, and rate-limit failures.
- Real-time quota tracking printed to the console on every API response.

---

## Project Structure

```
.
├── app.py          # Streamlit frontend — UI, session state, routing
├── backend.py      # API layer — IAC endpoint communication
├── get_api_key.py  # Utility for retrieving the API key
├── .env            # API key (not committed — see Security below)
└── requirements.txt
```

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd "Agentic Chat Bot"
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API key

Create a `.env` file in the project root:

```
API_KEY=your_iac_api_key_here
ID=your_iac_id_here
PASSWORD=your_iac_password_here
```

> ⚠️ **Security:** Make sure `.env` is listed in your `.gitignore` file so your key is never committed to version control.

---

## Running the App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`.

---

## Modes

### Stateless (Fast)
- Uses the `/chat/completions` endpoint.
- Maintains conversation history on the client side.
- Automatically trims history to the last 10 messages to avoid token overflow.

### Agentic (Web Search)
- Uses the `/responses` endpoint.
- Supports real-time web search via the `web_search` tool.
- Configurable system instructions and reasoning effort (`low` / `medium` / `high`).

---

## Environment Variables

| Variable   | Description                        |
|------------|------------------------------------|
| `API_KEY`  | Your IAC student API key           |
| `ID`       | Your IAC student ID                |
| `PASSWORD` | Your IAC account password          |

---

## Dependencies

| Package         | Purpose                          |
|-----------------|----------------------------------|
| `streamlit`     | Web UI framework                 |
| `requests`      | HTTP client for API calls        |
| `python-dotenv` | Loads `.env` into the environment|
