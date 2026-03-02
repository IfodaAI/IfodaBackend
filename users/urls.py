from django.urls import path, include
from rest_framework import routers
from .views import (
    UserViewSet,
    TelegramUserViewSet,
    BranchViewSet,
    RegionViewSet,
    DistrictViewSet,
    TelegramWebAppAuthView,
    MeView,
)

router = routers.DefaultRouter()

router.register(r"users", UserViewSet)
router.register(r"telegram-users", TelegramUserViewSet)
router.register(r"branches", BranchViewSet)
router.register(r"regions", RegionViewSet)
router.register(r"districts", DistrictViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # Telegram WebApp Auth
    path("auth/telegram/", TelegramWebAppAuthView.as_view(), name="telegram-auth"),
    path("auth/me/", MeView.as_view(), name="me"),
]
