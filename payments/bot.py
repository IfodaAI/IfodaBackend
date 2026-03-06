import logging

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_payment_success_message(telegram_id):
    """To'lov muvaffaqiyatli bo'lganda foydalanuvchiga Telegram xabar yuboradi."""
    text = (
        "To'lov muvaffaqiyatli amalga oshildi ✅ \n"
        "Buyurtma 24 soat ichida yetkazib beriladi 🚕\n\n"
        "🌱 <b>IFODA</b> - <b>Birgalikda yetishtiramiz!</b>"
    )
    try:
        requests.post(
            url=f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
            data={
                'chat_id': telegram_id,
                'text': text,
                'parse_mode': 'HTML'
            },
            timeout=5,
        )
    except Exception as e:
        logger.error(f"To'lovda Telegramga xabar yuborishda xatolik: {e}")
