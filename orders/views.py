from rest_framework.viewsets import ModelViewSet
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from products.models import ProductSKU
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer
from .permissions import OrderPermission

class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [OrderPermission]
    serializer_class = OrderSerializer

    def create(self, request:HttpRequest|Request, *args, **kwargs):
        # data split
        items=request.data.pop("items")
        order=request.data.pop("order")

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
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
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