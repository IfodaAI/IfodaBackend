import hashlib
import hmac
import json
import time
from urllib.parse import parse_qs, unquote

from django.conf import settings


class TelegramInitDataValidator:
    MAX_AGE_SECONDS = 300  # 5 daqiqa

    def __init__(self, bot_token: str = None):
        self.bot_token = bot_token or settings.TELEGRAM_BOT_TOKEN

    def validate(self, init_data: str) -> dict:
        """
        Telegram WebApp initData ni HMAC-SHA256 orqali tekshiradi.

        Algoritm (Telegram docs dan):
        1. Query string ni parse qilish
        2. 'hash' parametrini ajratib olish
        3. Qolgan parametrlarni alifbo tartibida saralash
        4. "key=value" formatida newline bilan birlashtirish
        5. secret_key = HMAC-SHA256("WebAppData", bot_token)
        6. hash = HMAC-SHA256(secret_key, data_check_string)
        7. Hisoblangan hash bilan olingan hash ni solishtirish

        Muvaffaqiyatli bo'lsa parsed data dict qaytaradi.
        Xatolik bo'lsa ValueError raise qiladi.
        """
        parsed = parse_qs(init_data, keep_blank_values=True)
        data = {k: v[0] for k, v in parsed.items()}

        if "hash" not in data:
            raise ValueError("hash parameter missing")

        received_hash = data.pop("hash")

        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(data.items())
        )

        secret_key = hmac.new(
            key=b"WebAppData",
            msg=self.bot_token.encode(),
            digestmod=hashlib.sha256,
        ).digest()

        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(calculated_hash, received_hash):
            raise ValueError("initData signature invalid")

        auth_date = int(data.get("auth_date", 0))
        if time.time() - auth_date > self.MAX_AGE_SECONDS:
            raise ValueError(f"initData expired (>{self.MAX_AGE_SECONDS}s)")

        if "user" in data:
            data["user"] = json.loads(unquote(data["user"]))

        return data
