"""
Page 3 — Dashboard

Shows four KPIs and two charts based on all feedback_requests rows.
Requires login.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from utils.auth import require_login
from utils.database import get_all_requests

st.set_page_config(page_title="Dashboard", layout="wide")

st.logo("static/uldre.png", link="https://uldre.no/om-uldre")

require_login()

st.title("Dashboard")

# --- Load data ---
rows = get_all_requests()

if not rows:
    st.info("Ingen data ennå. Send ut den første oppfølgingen fra 'Send oppfølging'.")
    st.stop()

df = pd.DataFrame(rows)
df["sent_at"] = pd.to_datetime(df["sent_at"], utc=True)
df["responded_at"] = pd.to_datetime(df["responded_at"], utc=True, errors="coerce")

# --- KPIs ---
total_sent = len(df)
total_responded = df["score"].notna().sum()
response_rate = (total_responded / total_sent * 100) if total_sent else 0
avg_score = df["score"].mean() if total_responded else 0
google_reviews = int(df["google_sms_sent"].sum())

col1, col2, col3, col4 = st.columns(4)
col1.metric("Totalt sendt", total_sent)
col2.metric("Svarprosent", f"{response_rate:.0f}%")
col3.metric("Snitt-score", f"{avg_score:.1f}" if total_responded else "—")
col4.metric("Google-anmeldelser sendt", google_reviews)

st.divider()

# --- Charts ---
responded_df = df[df["score"].notna()].copy()

if not responded_df.empty:
    chart_col1, chart_col2 = st.columns(2)

    # Chart 1: average score per week (line chart)
    with chart_col1:
        st.subheader("Snitt-score per uke")
        responded_df["week"] = responded_df["responded_at"].dt.to_period("W").apply(lambda r: r.start_time)
        weekly = responded_df.groupby("week")["score"].mean().reset_index()
        weekly.columns = ["Uke", "Snitt-score"]
        fig_line = px.line(
            weekly,
            x="Uke",
            y="Snitt-score",
            markers=True,
            range_y=[1, 5],
        )
        fig_line.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig_line, use_container_width=True)

    # Chart 2: score distribution (bar chart)
    with chart_col2:
        st.subheader("Scorefordeling")
        score_counts = (
            responded_df["score"]
            .value_counts()
            .reindex([1, 2, 3, 4, 5], fill_value=0)
            .reset_index()
        )
        score_counts.columns = ["Score", "Antall"]
        score_counts["Score"] = score_counts["Score"].astype(str)
        fig_bar = px.bar(score_counts, x="Score", y="Antall", text="Antall")
        fig_bar.update_layout(margin=dict(t=10, b=10))
        st.plotly_chart(fig_bar, use_container_width=True)
else:
    st.info("Ingen kunder har svart ennå — grafene vises når de første svarene kommer inn.")

st.divider()

# --- Full table ---
st.subheader("Alle utsendelser")

display_df = df[[
    "customer_name", "phone_number", "sent_at", "score", "responded_at",
    "google_sms_sent", "email_notified"
]].copy()

display_df.columns = [
    "Kundenavn", "Telefon", "Sendt", "Score", "Svart",
    "Google SMS sendt", "Epost varslet"
]

# Format timestamps for readability
display_df["Sendt"] = display_df["Sendt"].dt.strftime("%d.%m.%Y %H:%M")
display_df["Svart"] = display_df["Svart"].dt.strftime("%d.%m.%Y %H:%M").fillna("—")
display_df["Score"] = display_df["Score"].fillna("—").astype(str).str.replace(".0", "", regex=False)

st.dataframe(display_df, use_container_width=True, hide_index=True)
