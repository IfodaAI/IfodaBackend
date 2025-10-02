from django.urls import path, include

from rest_framework import routers

from .views import RoomViewSet, MessageViewSet

router = routers.DefaultRouter()

router.register(r"messages", MessageViewSet)
router.register(r"rooms", RoomViewSet)

urlpatterns = [path("", include(router.urls))]
