"""
Config helper — reads secrets from Streamlit Cloud (st.secrets) when available,
falls back to environment variables / .env for local development.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get(key: str) -> str:
    """Return a config value by key. Raises KeyError if not found anywhere."""
    # Try Streamlit secrets first (available when running on Streamlit Cloud)
    try:
        import streamlit as st
        return st.secrets[key]
    except Exception:
        pass

    value = os.environ.get(key)
    if value is None:
        raise KeyError(f"Config key '{key}' not found in st.secrets or environment.")
    return value
