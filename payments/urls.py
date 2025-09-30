# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PaymeWebhookView, ClickWebhookView
from django.urls import path, include

from rest_framework import routers

from .views import PaymentViewset, DeliveryViewset

router = routers.DefaultRouter()

router.register(r"payments", PaymentViewset)
router.register(r"deliveries", DeliveryViewset)

urlpatterns = [
    path("", include(router.urls)),
    path('payments/webhook/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/webhook/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
