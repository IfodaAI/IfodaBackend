import hashlib
import json
import logging
import os
import time
from datetime import datetime

from django.conf import settings

import requests
from paytechuz.integrations.django.views import (
    BasePaymeWebhookView,
    BaseClickWebhookView,
)
from orders.models import Order

logger = logging.getLogger(__name__)

class PaymentMixin:
    """Order status yangilash va fiskalatsiya uchun umumiy metodlar."""

    def _build_fiscal_items(self, order):
        """Payme va Click uchun umumiy fiskal mahsulot ro'yxatini yaratadi."""
        items = []
        for item in order.order_items.all():
            total_price = int(item.price * item.quantity * 100)  # tiyinlarda
            vat_percent = 12
            vat_amount = int(total_price * vat_percent / (100 + vat_percent))
            items.append({
                "title": item.product.product_name,
                "price": int(item.price * 100),
                "count": item.quantity,
                "code": item.product.product.spic,
                "vat_percent": vat_percent,
                "package_code": item.product.product.package_code,
                "total_price": total_price,
                "vat_amount": vat_amount,
            })
        return items

    def _submit_click_fiscal(self, transaction, order,params):
        """Click fiskal API ga mahsulot ma'lumotlarini yuboradi."""
        click_cfg = settings.PAYTECHUZ.get("CLICK", {})
        merchant_user_id = click_cfg.get("MERCHANT_USER_ID")
        secret_key = click_cfg.get("SECRET_KEY")
        service_id = click_cfg.get("SERVICE_ID")

        if not all([merchant_user_id, secret_key, service_id]):
            logger.error("Click fiskal: CLICK sozlamalari to'liq emas")
            return

        timestamp = str(int(time.time()))
        digest = hashlib.sha1(f"{timestamp}{secret_key}".encode()).hexdigest()
        auth_header = f"{merchant_user_id}:{digest}:{timestamp}"

        fiscal_items = self._build_fiscal_items(order)
        items_payload = []
        for fi in fiscal_items:
            items_payload.append({
                "Name": fi["title"],
                "SPIC": fi["code"],
                "PackageCode": fi["package_code"],
                "Price": fi["total_price"],
                "Amount": fi["count"],
                "VATPercent": fi["vat_percent"],
                "VAT": fi["vat_amount"],
                "CommissionInfo": {
                    "TIN": settings.TIN,
                },
            })

        total_amount = sum(fi["total_price"] for fi in fiscal_items)
        payload = {
            "service_id": int(service_id),
            "payment_id": int(params.get('click_paydoc_id')),
            "items": items_payload,
            "received_ecash": total_amount,
            "received_cash": 0,
            "received_card": 0,
        }

        url = "https://api.click.uz/v2/merchant/payment/ofd_data/submit_items"
        req_headers = {
            "Auth": auth_header,
            "Accept":"application/json",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                url=url,
                json=payload,
                headers=req_headers,
                timeout=10,
            )
            result = response.json()

            # Log to file
            log_dir = os.path.join(settings.BASE_DIR, "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "click_fiscal.log")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"[{datetime.now().isoformat()}]\n")
                f.write(f"--- REQUEST ---\n")
                f.write(f"URL: {url}\n")
                f.write(f"Headers: {json.dumps(req_headers, ensure_ascii=False, indent=2)}\n")
                f.write(f"Payload: {json.dumps(payload, ensure_ascii=False, indent=2)}\n")
                f.write(f"--- RESPONSE ---\n")
                f.write(f"Status: {response.status_code}\n")
                f.write(f"Headers: {json.dumps(dict(response.headers), ensure_ascii=False, indent=2)}\n")
                f.write(f"Body: {json.dumps(result, ensure_ascii=False, indent=2)}\n")
                f.write(f"{'='*80}\n")

            if result.get("error_code", -1) != 0:
                logger.error(f"Click fiskal xatolik: {result}")
            else:
                logger.info(f"Click fiskal muvaffaqiyatli: payment_id={transaction.transaction_id}")
        except Exception as e:
            logger.error(f"Click fiskal API ga so'rov yuborishda xatolik: {e}")

    def _update_order_status(self, transaction, status, params=None):
        try:
            order = Order.objects.get(id=transaction.account_id)
        except Order.DoesNotExist:
            logger.error(f"Order topilmadi: account_id={transaction.account_id}")
            return
        order.status = status
        order.save()
        if status=="PROCESSING":
            text = """To'lov muvaffaqiyatli amalga oshildi ✅
Buyurtma 24 soat ichida yetkazib beriladi.
Ishonchingiz uchun minnatdormiz
IFODA kompaniyasini tanlaganingizdan mamnunmiz
Birgalikda yetishtiramiz!✅"""
            try:
                requests.post(
                    url=f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                    data={
                        'chat_id': order.user.telegram_id,
                        'text': text,
                        'parse_mode': 'HTML'
                    },
                    timeout=5,
                ).json()
            except Exception as e:
                logger.error(f"To'lovda Telegramga xabar yuborishda xatolik: {e}")

class PaymeWebhookView(PaymentMixin, BasePaymeWebhookView):
    def before_check_perform_transaction(self, params, account):
        order_id = params["account"]["order_id"]
        order = Order.objects.get(id=order_id)
        fiscal_items = self._build_fiscal_items(order)
        data = {"allow": True, "detail": {"receipt_type": 0, "items": []}}
        for fi in fiscal_items:
            data["detail"]["items"].append({
                "discount": 0,
                "title": fi["title"],
                "price": fi["price"],
                "count": fi["count"],
                "code": fi["code"],
                "vat_percent": fi["vat_percent"],
                "package_code": fi["package_code"],
            })
        return data

    def _check_perform_transaction(self, params):
        account = self._find_account(params)
        self._validate_amount(account, params.get("amount"))
        return self.before_check_perform_transaction(params, account) or {"allow": True}

    def successfully_payment(self, params, transaction):
        self._update_order_status(transaction, "PROCESSING", params)

    def cancelled_payment(self, params, transaction):
        self._update_order_status(transaction, "REJECTED", params)


class ClickWebhookView(PaymentMixin, BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        self._update_order_status(transaction, "PROCESSING", params)
        try:
            order = Order.objects.get(id=transaction.account_id)
            self._submit_click_fiscal(transaction, order,params)
        except Order.DoesNotExist:
            logger.error(f"Click fiskal: Order topilmadi: account_id={transaction.account_id}")

    def cancelled_payment(self, params, transaction):
        self._update_order_status(transaction, "REJECTED", params)
