from utils.serializers import BaseModelSerializer
from .models import Order, OrderItem, Delivery
from django.http import HttpRequest
from products.serializers import ProductSKUSerializer

class OrderSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Order

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
            product_sku = request.GET.get("product_sku")
            if product_sku == "true":
                self.fields["product_sku"] = ProductSKUSerializer(context=self.context)


class DeliverySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Delivery
