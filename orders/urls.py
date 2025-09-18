from django.urls import path, include

from rest_framework import routers

from .views import OrderViewSet, OrderItemsViewSet

router = routers.DefaultRouter()

router.register(r"orders", OrderViewSet)
router.register(r"order-items", OrderItemsViewSet)

urlpatterns = [path("", include(router.urls))]
