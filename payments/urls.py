# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from .views import PaymeWebhookView, ClickWebhookView
from django.urls import path

urlpatterns = [
    path('payments/webhook/payme/', csrf_exempt(PaymeWebhookView.as_view()), name='payme_webhook'),
    path('payments/webhook/click/', csrf_exempt(ClickWebhookView.as_view()), name='click_webhook'),
]
