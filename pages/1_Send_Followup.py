"""
Page 1 — Send Follow-up

The manager fills in customer name and phone number, then clicks "Send oppfølging".
The app:
  1. Inserts a new row in feedback_requests (gets back a unique token).
  2. Sends an SMS to the customer with the feedback link.
"""

import streamlit as st
from utils.auth import require_login
from utils.database import insert_feedback_request
from utils.sms import send_feedback_request

st.set_page_config(page_title="Send oppfølging", layout="centered")

st.logo("static/uldre.png", link="https://uldre.no/om-uldre")

require_login()

st.title("Send oppfølging")

with st.form("send_form", clear_on_submit=True):
    customer_name = st.text_input("Kundenavn")
    phone_number = st.text_input("Telefonnummer", placeholder="4712345678")
    submitted = st.form_submit_button("Send oppfølging")

if submitted:
    if not customer_name.strip():
        st.error("Fyll inn kundenavn.")
    elif not phone_number.strip():
        st.error("Fyll inn telefonnummer.")
    else:
        try:
            row = insert_feedback_request(customer_name.strip(), phone_number.strip())
            send_feedback_request(customer_name.strip(), phone_number.strip(), row["token"])
            st.success(f"SMS sendt til {customer_name} ({phone_number}).")
        except Exception as e:
            st.error(f"Noe gikk galt: {e}")
