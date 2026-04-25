"""
Page 2 — Customer Feedback (public, no login required)

Opened via the SMS link: .../Feedback?token=<uuid>

Flow:
  - Load the row by token. If missing or already answered → show appropriate message.
  - Customer picks a score 1–5.
  - Score 4-5 → send Google review SMS, then save score + flag in one DB call.
  - Score 1-3 → send email alert to manager, then save score + flag in one DB call.
"""

import streamlit as st
from utils.database import get_request_by_token, submit_score
from utils.sms import send_google_review_request
from utils.email_notify import send_low_score_alert

st.set_page_config(page_title="Tilbakemelding", layout="centered")

st.logo("static/uldre.png", link="https://uldre.no/om-uldre")

st.markdown("""
    <style>
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- Read token from URL query params ---
params = st.query_params
token = params.get("token", "")

if not token:
    st.error("Ugyldig lenke. Ingen token funnet.")
    st.stop()

# --- Load the feedback request ---
row = get_request_by_token(token)

if row is None:
    st.error("Lenken er ugyldig eller utløpt.")
    st.stop()

if row["score"] is not None:
    st.info("Du har allerede sendt inn din tilbakemelding. Takk!")
    st.stop()

# --- Show score form ---
customer_name = row["customer_name"]
phone_number = row["phone_number"]

st.title(f"Hei, {customer_name}!")
st.write("Hvor fornøyd er du med jobben vi utførte?")

score = st.radio(
    "Velg din score:",
    options=[1, 2, 3, 4, 5],
    format_func=lambda x: {1: "1 — Svært misfornøyd", 2: "2 — Misfornøyd", 3: "3 — Nøytral", 4: "4 — Fornøyd", 5: "5 — Svært fornøyd"}[x],
    horizontal=True,
)

if st.button("Send inn"):
    try:
        # Attempt notifications before saving — flags reflect what actually succeeded
        google_sms_sent = False
        email_notified = False

        if score >= 4:
            try:
                send_google_review_request(customer_name, phone_number)
                google_sms_sent = True
            except Exception:
                pass  # don't block the thank-you page if SMS fails
        else:
            try:
                send_low_score_alert(customer_name, phone_number, score)
                email_notified = True
            except Exception as email_err:
                st.warning(f"E-post feilet: {email_err}")

        # Save everything in one DB call (single anon UPDATE allowed by RLS)
        submit_score(token, score, google_sms_sent=google_sms_sent, email_notified=email_notified)

        st.success("Takk for tilbakemeldingen! Vi setter stor pris på det.")
        st.balloons()

    except ValueError:
        st.warning("Du har allerede sendt inn din tilbakemelding.")
    except Exception as e:
        st.error(f"Noe gikk galt: {e}")
