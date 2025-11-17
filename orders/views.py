from django.http import HttpRequest

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

from users.models import Branch
from products.models import ProductSKU
from .models import Order, OrderItem, Delivery
from .serializers import OrderSerializer, OrderItemSerializer, DeliverySerializer
from .permissions import OrderPermission
from django.conf import settings

from utils.utils import get_distance_from_lat_lon_in_km

class DeliveryViewset(ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [OrderPermission]
    serializer_class = OrderSerializer

    # ✅ Yagona payment generator
    def generate_payment_link(self, gateway_name, data):
        cfg = settings.PAYTECHUZ[gateway_name.upper()]

        if gateway_name == "payme":
            gateway = PaymeGateway(
                payme_id=cfg["PAYME_ID"],
                payme_key=cfg["PAYME_KEY"],
                is_test_mode=cfg["IS_TEST_MODE"],
            )
            return gateway.create_payment(id=data["id"], amount=data["amount"])

        elif gateway_name == "click":
            gateway = ClickGateway(
                service_id=cfg["SERVICE_ID"],
                merchant_id=cfg["MERCHANT_ID"],
                merchant_user_id=cfg["MERCHANT_USER_ID"],
                secret_key=cfg["SECRET_KEY"],
                is_test_mode=cfg["IS_TEST_MODE"],
            )
            return gateway.create_payment(
                id=data["id"], amount=data["amount"], description=str(cfg["MERCHANT_USER_ID"])
            )

        raise ValueError(f"Unknown payment method: {gateway_name}")

    @action(detail=True, methods=['get'])
    def payment_link(self, request:Request|HttpRequest, pk=None):
        order = self.get_object()
        # ✅ To‘lov havolasi
        payment_method = request.GET.get("payment_method")
        if order.delivery_method == "DELIVERY" and payment_method in ("payme", "click"):
            payment_link = self.generate_payment_link(payment_method, {"id":order.id,"amount":order.amount})
            if payment_link:
                return Response(payment_link)
        return Response(
                {"detail": f"To'lov havolasini generatsiya qilishda xatolik."},
                status=status.HTTP_400_BAD_REQUEST
            )

    def create(self, request: HttpRequest, *args, **kwargs):
        data = {}
        items = request.data.pop("items", [])
        order_data = request.data.pop("order", {})

        # ✅ Branch aniqlash
        branch_id = order_data.get("branch")
        if branch_id:
            branch = Branch.objects.get(id=branch_id)
            order_data["delivery_latitude"] = branch.latitude
            order_data["delivery_longitude"] = branch.longitude
        else:
            user_lat = float(order_data.get("delivery_latitude"))
            user_lon = float(order_data.get("delivery_longitude"))
            payment_method = order_data.get("payment_method")

            nearest_branch = min(
                Branch.objects.all(),
                key=lambda b: get_distance_from_lat_lon_in_km(
                    user_lat, user_lon, b.latitude, b.longitude
                ),
            )
            order_data["branch"] = nearest_branch.id

        # ✅ Order yaratish
        order_data["user"] = request.user.id
        serializer = self.get_serializer(data=order_data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # ✅ Itemlar yaratish va summani hisoblash
        total_amount = 0
        for item in items:
            product = ProductSKU.objects.get(id=item["product"])
            order_item = OrderItem(order=order, product=product, **item)
            order_item.save()
            total_amount += order_item.price

        # ✅ Yakuniy summa
        order.amount = total_amount
        order.save(update_fields=["amount"])

        # ✅ To‘lov havolasi
        payment_link = None
        payment_method = order_data.get("payment_method")
        if order.delivery_method == "DELIVERY" and payment_method in ("payme", "click"):
            payment_link = self.generate_payment_link(payment_method, serializer.data)

        data["order"] = serializer.data
        if payment_link:
            data["payment_link"] = payment_link

        return Response(data, status=status.HTTP_201_CREATED)

    def perform_update(self, serializer):
        user = self.request.user
        order = self.get_object()

        if user.role == "MANAGER" and order.branch_id != user.branch_id:
            raise PermissionDenied("Siz faqat o‘z filialingizdagi buyurtmalarni tahrirlashingiz mumkin.")
        if user.role == "DISPATCHER":
            raise PermissionDenied("Dispetcherlar uchun faqat o‘qish huquqi bor.")
        serializer.save()

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.role == "ADMIN":
            return Order.objects.all()
        if user.role == "MANAGER":
            return Order.objects.filter(branch_id=user.branch_id)
        if user.role == "DISPATCHER":
            return Order.objects.all()
        return Order.objects.filter(user=user)

class OrderItemsViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
