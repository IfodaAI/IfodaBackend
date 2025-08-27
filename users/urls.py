from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, TelegramUserViewSet, BranchViewSet

router = routers.DefaultRouter()

router.register(r"users", UserViewSet)
router.register(r"telegram-users", TelegramUserViewSet)
router.register(r"branches", BranchViewSet)

urlpatterns = [path("", include(router.urls))]
