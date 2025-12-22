import requests
from django.conf import settings
import json


def send_telegram_message(chat_id: int | str, text: str):
    """
    Telegram user yoki guruhga xabar yuboradi
    """
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # log qilish tavsiya etiladi
        print("Telegram error:", e)
        return None

def send_telegram_message_with_button(chat_id, text, button_text, webapp_url):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps({
            "inline_keyboard": [
                [
                    {
                        "text": button_text,
                        "web_app": {"url": webapp_url}
                    }
                ]
            ]
        })
    }

    requests.post(url, data=payload)