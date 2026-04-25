"""
Supabase email/password authentication helpers for Streamlit.

Usage pattern in any protected page:
    from utils.auth import require_login
    require_login()   # stops rendering and shows login form if not authenticated
"""

import streamlit as st
from supabase import create_client
from utils.config import get


def _client():
    return create_client(get("SUPABASE_URL"), get("SUPABASE_ANON_KEY"))


def require_login() -> None:
    """
    Gate for protected pages. If the user is not logged in, show a login form
    and stop the rest of the page from rendering via st.stop().
    """
    if "user" not in st.session_state:
        st.session_state["user"] = None

    if st.session_state["user"] is not None:
        return  # already logged in — let the page continue

    st.title("Logg inn")
    email = st.text_input("E-post")
    password = st.text_input("Passord", type="password")

    if st.button("Logg inn"):
        try:
            client = _client()
            result = client.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            st.session_state["user"] = result.user
            st.session_state["access_token"] = result.session.access_token
            st.rerun()
        except Exception as e:
            st.error(f"Innlogging mislyktes: {e}")

    st.stop()  # prevent the rest of the page from rendering


def logout() -> None:
    """Clear the session and rerun."""
    st.session_state["user"] = None
    st.session_state["access_token"] = None
    try:
        _client().auth.sign_out()
    except Exception:
        pass
    st.rerun()
