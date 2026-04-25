"""
SMS sending via Sveve API.
"""

import requests
from utils.config import get

_SVEVE_URL = "https://sveve.no/SMS/SendMessage"


def _send(to: str, message: str) -> None:
    phone = to.lstrip("+")
    if len(phone) == 8:
        phone = "47" + phone
    # SVEVE_API_KEY format: "username:password"
    api_key = get("SVEVE_API_KEY")
    user, passwd = api_key.split(":", 1)

    response = requests.get(
        _SVEVE_URL,
        params={
            "user": user,
            "passwd": passwd,
            "to": phone,
            "from": get("SVEVE_SENDER"),
            "msg": message,
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    if data.get("response", {}).get("fatalError"):
        raise RuntimeError(f"Sveve feil: {data['response']['fatalError']}")


def send_feedback_request(customer_name: str, phone_number: str, token: str) -> None:
    base_url = get("APP_BASE_URL").rstrip("/")
    link = f"{base_url}/Feedback?token={token}"
    message = (
        f"Hei {customer_name}! Takk for at du valgte oss. "
        f"Vi setter stor pris på din tilbakemelding — det tar bare 10 sekunder: {link}"
    )
    _send(phone_number, message)


def send_google_review_request(customer_name: str, phone_number: str) -> None:
    google_url = get("GOOGLE_REVIEW_URL")
    message = (
        f"Hei {customer_name}! Så hyggelig at du er fornøyd. "
        f"Vil du hjelpe oss ved å legge igjen en Google-anmeldelse? Det betyr mye: {google_url}"
    )
    _send(phone_number, message)
