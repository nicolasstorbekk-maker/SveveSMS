"""
Database helpers — all Supabase calls go through this module.

One client with the anon key is used everywhere:
- Manager operations pass the session access_token so Supabase RLS recognises
  them as an authenticated user and grants full access.
- Public feedback page calls work without a token; RLS allows anonymous users
  to read by token and submit a score exactly once.
"""

from datetime import datetime, timezone
from supabase import create_client, Client
from utils.config import get

TABLE = "feedback_requests"


def _client(session_token: str | None = None) -> Client:
    client = create_client(get("SUPABASE_URL"), get("SUPABASE_ANON_KEY"))
    if session_token:
        client.postgrest.auth(session_token)
    return client


def _manager_client() -> Client:
    """Client authenticated with the logged-in manager's session token."""
    import streamlit as st
    token = st.session_state.get("access_token")
    return _client(session_token=token)


# ---------------------------------------------------------------------------
# Manager operations (authenticated via session token)
# ---------------------------------------------------------------------------

def insert_feedback_request(customer_name: str, phone_number: str) -> dict:
    """
    Insert a new feedback request row. Returns the created row (including the
    generated token and id) so the caller can build the SMS link.
    """
    response = (
        _manager_client()
        .table(TABLE)
        .insert({"customer_name": customer_name, "phone_number": phone_number})
        .execute()
    )
    return response.data[0]


def get_all_requests() -> list[dict]:
    """Return all rows ordered by sent_at descending, for the dashboard."""
    response = (
        _manager_client()
        .table(TABLE)
        .select("*")
        .order("sent_at", desc=True)
        .execute()
    )
    return response.data


# ---------------------------------------------------------------------------
# Public feedback page operations (anon, RLS enforced)
# ---------------------------------------------------------------------------

def get_request_by_token(token: str) -> dict | None:
    """
    Fetch a single feedback request by its token.
    Returns None if not found.
    """
    response = (
        _client()
        .table(TABLE)
        .select("id, customer_name, phone_number, score")
        .eq("token", token)
        .execute()
    )
    if not response.data:
        return None
    return response.data[0]


def submit_score(
    token: str,
    score: int,
    google_sms_sent: bool = False,
    email_notified: bool = False,
) -> dict:
    """
    Record the customer's score and set notification flags in a single update.
    Only succeeds if score has not already been submitted (enforced by RLS).
    Returns the updated row.
    """
    response = (
        _client()
        .table(TABLE)
        .update({
            "score": score,
            "responded_at": datetime.now(timezone.utc).isoformat(),
            "google_sms_sent": google_sms_sent,
            "email_notified": email_notified,
        })
        .eq("token", token)
        .is_("score", "null")   # prevent re-voting
        .execute()
    )
    if not response.data:
        raise ValueError("Score already submitted or token not found.")
    return response.data[0]
