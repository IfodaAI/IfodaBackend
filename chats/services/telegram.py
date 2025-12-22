import requests
from django.conf import settings


def send_telegram_message(chat_id: int | str, text: str, parse_mode: str="HTML"):
    """
    Telegram user yoki guruhga xabar yuboradi
    """
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }

    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        # log qilish tavsiya etiladi
        print("Telegram error:", e)
        return None
