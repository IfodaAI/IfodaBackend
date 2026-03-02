import json
import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


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
        logger.error(f"Telegram xabar yuborishda xatolik: {e}")
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

    try:
        r = requests.post(url, data=payload, timeout=5)
        r.raise_for_status()
        result = r.json()
        return result.get("result", {}).get("message_id")
    except requests.RequestException as e:
        logger.error(f"Telegram tugmali xabar yuborishda xatolik: {e}")
        return None

def delete_telegram_message(chat_id, message_id):
    token = settings.TELEGRAM_BOT_TOKEN
    url = f"https://api.telegram.org/bot{token}/deleteMessage"

    params = {
        "chat_id": chat_id,
        "message_id": message_id
    }
    try:
        requests.post(url, data=params, timeout=5)
    except requests.RequestException as e:
        logger.error(f"Telegram xabar o'chirishda xatolik: {e}")
