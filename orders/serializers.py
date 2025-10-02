from utils.serializers import BaseModelSerializer
from .models import Order, OrderItem, Delivery


class OrderSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Order


class OrderItemSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = OrderItem


class DeliverySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Delivery
