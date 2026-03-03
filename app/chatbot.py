import os
import sys
import json
import tempfile

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

# ── GCP / Vertex AI configuration ──────────────────────────────────────────
GCP_PROJECT_ID = st.secrets["gcp"]["project_id"]
GCP_LOCATION   = "us-central1"

# Write GCP credentials from Streamlit secrets to a temp file
_credentials_dict = dict(st.secrets["gcp"]["credentials"])
_tmp = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
json.dump(_credentials_dict, _tmp)
_tmp.close()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _tmp.name
os.environ["GOOGLE_GENAI_USE_VERTEXAI"]      = "1"
os.environ["GOOGLE_CLOUD_PROJECT"]           = GCP_PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"]          = GCP_LOCATION

import vertexai
vertexai.init(project=GCP_PROJECT_ID, location=GCP_LOCATION)

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

#from tools import query_financials, query_properties, query_press_releases
from tools import query_financials, query_properties, query_press_releases, query_sec_filings

# ── Build the ADK Agent ─────────────────────────────────────────────────────
financial_agent = Agent(
    name="financial_assistant",
    model="gemini-2.0-flash",
    instruction="""You are an expert financial assistant for a real estate investment company.

You have access to three tools:
- query_financials: use for revenue, net income, or expense questions
- query_properties: use for questions about specific properties, metro areas, or property types
- query_press_releases: use for questions about company news, acquisitions, or announcements
- query_sec_filings: use for questions about SEC filings, official reported revenue, 10-K or 10-Q earnings data


When answering:
- Call the relevant tool(s) first, then summarize the results in clear, professional language
- You may call more than one tool if the question spans multiple data sources
- Format currency values with dollar signs and commas
- If nothing matches, say so honestly
""",
    tools=[query_financials, query_properties, query_press_releases, query_sec_filings],
)

# ── Session & Runner setup ──────────────────────────────────────────────────
_session_service = InMemorySessionService()
_APP_NAME        = "financial_assistant"
_USER_ID         = "streamlit_user"

_runner = Runner(
    agent=financial_agent,
    app_name=_APP_NAME,
    session_service=_session_service,
)


import asyncio
import threading

_sessions_created = set()

def _ensure_session(session_id: str):
    """Create the session in a fresh event loop to avoid conflicts with Streamlit."""
    if session_id in _sessions_created:
        return

    def create_in_new_loop():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(
                _session_service.create_session(
                    app_name=_APP_NAME,
                    user_id=_USER_ID,
                    session_id=session_id,
                )
            )
        finally:
            loop.close()

    t = threading.Thread(target=create_in_new_loop)
    t.start()
    t.join()

    _sessions_created.add(session_id)



def handle_query(user_query: str, session_id: str = "main") -> str:
    """
    Send a natural language question to the Vertex AI ADK agent
    and return its response.
    """
    _ensure_session(session_id)

    message = types.Content(
        role="user",
        parts=[types.Part(text=user_query)],
    )

    try:
        response_text = ""
        for event in _runner.run(
            user_id=_USER_ID,
            session_id=session_id,
            new_message=message,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    response_text = event.content.parts[0].text
                break

        return response_text or "I couldn't generate a response. Please try again."

    except Exception as e:
        return f"⚠️ Error: {type(e).__name__}: {e}"