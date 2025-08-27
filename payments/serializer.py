from rest_framework.serializers import ModelSerializer
from .models import Payment, Delivery


class PaymentSerializer(ModelSerializer):
    class Meta:
        model = Payment
        fields = "__all__"

class DeliverySerializer(ModelSerializer):
    class Meta:
        model = Delivery
        fields = "__all__"
