from rest_framework.viewsets import ModelViewSet
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from products.models import ProductSKU
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .permissions import OrderPermission
from paytechuz.gateways.payme import PaymeGateway
from paytechuz.gateways.click import ClickGateway

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [OrderPermission]
    serializer_class = OrderSerializer

    def payme_gen(self,data):
        payme = PaymeGateway(
            payme_id="6881b7acd5ee42a97c8b6eff",
            payme_key="HJX&ESmd&ZJbZgGjuYii0uXMePcuuoHSVBN?",
            is_test_mode=False
            )
        return payme.create_payment(
            id=data['id'],
            amount=data['amount'],
            return_url="https://webapp.ifoda-shop.uz"
        )
    
    def click_gen(self,data):
        click = ClickGateway(
            service_id="79480",
            merchant_id="30842",
            merchant_user_id="48273",
            secret_key="KbcSKFP7TDVe",
            is_test_mode=False
        )
        return click.create_payment(
            id=data['id'],
            amount=data['amount'],
            return_url="https://webapp.ifoda-shop.uz",
            description="48273"
        )

    def create(self, request:HttpRequest|Request, *args, **kwargs):
        # data split
        items=request.data.pop("items")
        order:dict=request.data.pop("order")
        payment_method=order.pop("payment_method")

        # order create
        total_price=0
        order["user"]=request.user.id
        serializer = self.get_serializer(data=order)
        serializer.is_valid(raise_exception=True)
        order=self.perform_create(serializer)

        # item create
        for item in items:
            item["product"]=ProductSKU.objects.get(id=item["product"])
            order_item=OrderItem(order=order,**item)
            order_item.save()
            print(order_item.product)
            total_price+=order_item.price
        
        # total_price change
        order.total_price=total_price
        order.save()
        if payment_method == 'payme':
            payment_link=self.payme_gen(serializer.data)
        else:
            payment_link=self.click_gen(serializer.data)

        headers = self.get_success_headers(serializer.data)
        return Response({
            "payment_link":payment_link,
            "order":serializer.data
            }, 
        status=status.HTTP_201_CREATED, headers=headers)
    
    def perform_create(self, serializer):
        return serializer.save()

    def get_queryset(self):
        user = self.request.user

        # If user's role is admin, send all orders
        if user.is_superuser or user.role == "ADMIN":
            return Order.objects.all()

        # If user's role is manager, send only orders assigned to their branch.
        if user.role == "MANAGER":
            return Order.objects.filter(branch_id=user.branch_id)

        # If user's role is dispatcher, send all orders (read-only enforced by permission)
        if user.role == "DISPATCHER":
            return Order.objects.all()

        # If it's normal user, send only only their own orders.
        return Order.objects.filter(user=user)

    def perform_update(self, serializer):
        # extra safety: prevent manager updating orders of other branches
        user = self.request.user
        order = self.get_object()
        if user.role == "MANAGER" and order.branch_id != user.branch_id:
            raise PermissionDenied("You can only update orders for your branch.")
        
        # Dispatcher shouldn't reach here because permission blocks non-safe methods,
        # but extra protection is okay
        if user.role == "DISPATCHER":
            raise PermissionDenied("Dispatchers are read-only.")
        serializer.save()

class OrderItemsViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer