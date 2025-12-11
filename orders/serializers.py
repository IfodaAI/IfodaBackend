from utils.serializers import BaseModelSerializer
from .models import Order, OrderItem, Delivery
from django.http import HttpRequest
from products.serializers import ProductSKUSerializer
from rest_framework import serializers

class OrderSerializer(BaseModelSerializer):
    user_fullname = serializers.SerializerMethodField()
    payment_gateway = serializers.SerializerMethodField()
    branch_name = serializers.SerializerMethodField()

    class Meta(BaseModelSerializer.Meta):
        model = Order
    
    def get_user_fullname(self, obj):
        if obj.user:
            # Agar custom User modelda full_name bo'lsa
            if hasattr(obj.user, "get_full_name"):
                return obj.user.get_full_name()
            # fallback
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return None
    
    def get_payment_gateway(self, obj):
        return obj.get_payment_gateway
    
    def get_branch_name(self, obj):
        if obj.branch:
            return obj.branch.name
        return None

    def __init__(self, *args, **kwargs):
        super(OrderSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")
        if request and request.method == "GET":
            order_items = request.GET.get("order_items")
            if order_items == "true":
                self.fields["order_items"] = OrderItemSerializer(context=self.context,many=True)

class OrderItemSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = OrderItem
    
    def __init__(self, *args, **kwargs):
        super(OrderItemSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")
        if request and request.method == "GET":
            product = request.GET.get("product")
            if product == "true":
                self.fields["product"] = ProductSKUSerializer(context=self.context)


class DeliverySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Delivery
