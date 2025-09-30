from rest_framework.viewsets import ModelViewSet
from .models import Payment, Delivery
from .serializer import PaymentSerializer, DeliverySerializer
from rest_framework.permissions import AllowAny


class DeliveryViewset(ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer


class PaymentViewset(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer

from paytechuz.integrations.django.views import BasePaymeWebhookView, BaseClickWebhookView
from orders.models import Order

class PaymentMixin:
    """Order status yangilash uchun umumiy metod."""
    def _update_order_status(self, transaction, status, params=None):
        order = Order.objects.get(id=transaction.account_id)
        order.status = status
        order.save()
        print(f"Order {order.id} {status} — params: {params}, txn_id: {transaction.id}", flush=True)

class PaymeWebhookView(PaymentMixin, BasePaymeWebhookView):
    def before_check_perform_transaction(self, params, account):
        order_id=params["account"]["order_id"]
        order=Order.objects.get(id=order_id)
        data={
            'allow': True,
            "detail": {
                "receipt_type": 0,
                "items": []
            }
        }
        # for item in order.order_items:
        #     data['detail']["items"].append({
        #                 "discount": 0,
        #                 "title": "Мин.угит IFO UAN-32 0.2 л",#item.product.product_name,#
        #                 "price": 2000 * 100,  # tiyinlarda
        #                 "count": 1,
        #                 "code": "03105001001000000",
        #                 "vat_percent": 12,
        #                 "package_code": "1248694"
        #             })
        return data

    def _check_perform_transaction(self, params):
        account = self._find_account(params)
        self._validate_amount(account, params.get('amount'))
        return self.before_check_perform_transaction(params, account) or {'allow': True}

    def successfully_payment(self, params, transaction):
        self._update_order_status(transaction, 'paid', params)

    def cancelled_payment(self, params, transaction):
        self._update_order_status(transaction, 'cancelled', params)


class ClickWebhookView(PaymentMixin, BaseClickWebhookView):
    def successfully_payment(self, params, transaction):
        self._update_order_status(transaction, 'paid', params)

    def cancelled_payment(self, params, transaction):
        self._update_order_status(transaction, 'cancelled', params)