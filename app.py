"""
app.py — entry point for the Streamlit app.

This page acts as a home/landing page and handles the top-level navigation.
Protected pages redirect to login via utils/auth.py.

The public Feedback page (pages/2_Feedback.py) intentionally does NOT call
require_login() — it must be accessible by customers without an account.
"""

import streamlit as st
from utils.auth import require_login, logout

st.set_page_config(
    page_title="SMS Oppfølging",
    page_icon="📱",
    layout="centered",
)

st.logo("static/uldre.png", link="https://uldre.no/om-uldre")

require_login()

st.title("SMS Kundeoppfølging")
st.write("Velg en side i menyen til venstre.")

if st.button("Logg ut"):
    logout()
