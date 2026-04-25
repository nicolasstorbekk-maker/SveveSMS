"""
Email notification to the manager when a customer submits a low score (1-3).
Uses standard SMTP — works with Gmail app passwords, Mailgun SMTP, etc.
"""

import smtplib
from email.mime.text import MIMEText
from utils.config import get


def send_low_score_alert(customer_name: str, phone_number: str, score: int) -> None:
    """
    Send an email to the manager notifying them of a low score.
    """
    manager_email = get("MANAGER_EMAIL")
    smtp_host = get("SMTP_HOST")
    smtp_port = int(get("SMTP_PORT"))
    smtp_user = get("SMTP_USER")
    smtp_password = get("SMTP_PASSWORD")

    subject = f"Lav score fra kunde — {customer_name} ga {score}/5"
    body = (
        f"En kunde har gitt lav tilbakemelding.\n\n"
        f"Kunde:       {customer_name}\n"
        f"Telefon:     {phone_number}\n"
        f"Score:       {score}/5\n\n"
        f"Vi anbefaler at du tar kontakt med kunden for å løse eventuelle problemer."
    )

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = manager_email

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, [manager_email], msg.as_string())
