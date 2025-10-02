from django.urls import path, include

from rest_framework import routers

from .views import OrderViewSet, OrderItemsViewSet, DeliveryViewset

router = routers.DefaultRouter()

router.register(r"orders", OrderViewSet)
router.register(r"order-items", OrderItemsViewSet)
router.register(r"deliveries", DeliveryViewset)

urlpatterns = [path("", include(router.urls))]
