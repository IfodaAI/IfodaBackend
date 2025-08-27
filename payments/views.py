from rest_framework.viewsets import ModelViewSet
from .models import Payment, Delivery
from .serializer import PaymentSerializer, DeliverySerializer


class DeliveryViewset(ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer


class PaymentViewset(ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
