from paytechuz.integrations.django.views import (
    BasePaymeWebhookView,
    BaseClickWebhookView,
)
# from paytechuz.integrations.django.models import PaymentTransaction
from orders.models import Order
import requests
from django.conf import settings

class PaymentMixin:
    """Order status yangilash uchun umumiy metod."""

    def _update_order_status(self, transaction, status, params=None):
        order = Order.objects.get(id=transaction.account_id)
        order.status = status
        order.save()
        if status=="":
            text = """To'lov muvaffaqiyatli amalga oshildi ✅
            Buyurtma 24 soat ichida yetkazib beriladi.
            Ishonchingiz uchun minnatdormiz
            IFODA kompaniyasini tanlaganingizdan mamnunmiz
            Birgalikda yetishtiramiz!
            ✅"""
            try:
                requests.post(
                    url=f'https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage',
                    data={
                        'chat_id': order.user.telegram_id,
                        'text': text,
                        'parse_mode': 'HTML'
                    }
                ).json()
            except Exception as e:
                print('To\'lovda Telegramga xabar yuborishda xatolik yuz berdi: ', e)

class PaymeWebhookView(PaymentMixin, BasePaymeWebhookView):
    def before_check_perform_transaction(self, params, account):
        order_id = params["account"]["order_id"]
        order = Order.objects.get(id=order_id)
        data = {"allow": True, "detail": {"receipt_type": 0, "items": []}}
        for item in order.order_items.all():
            data["detail"]["items"].append(
                {
                    "discount": 0,
                    "title": item.product.product_name,
                    "price": item.price * 100,  # tiyinlarda
                    "count": 1,
                    "code": "03105001001000000",
                    "vat_percent": 12,
                    "package_code": "1248694",
                }
            )
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

    def cancelled_payment(self, params, transaction):
        self._update_order_status(transaction, "REJECTED", params)
