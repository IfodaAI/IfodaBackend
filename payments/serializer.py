from utils.serializers import BaseModelSerializer
from .models import Payment, Delivery


class PaymentSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Payment


class DeliverySerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Delivery
