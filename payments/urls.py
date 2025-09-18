from django.urls import path, include

from rest_framework import routers

from .views import PaymentViewset, DeliveryViewset

router = routers.DefaultRouter()

router.register(r"payments", PaymentViewset)
router.register(r"deliveries", DeliveryViewset)

urlpatterns = [path("", include(router.urls))]
