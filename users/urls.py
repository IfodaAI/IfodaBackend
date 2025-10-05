from django.urls import path, include
from rest_framework import routers
from .views import UserViewSet, TelegramUserViewSet, BranchViewSet, RegionViewSet, DistrictViewSet

router = routers.DefaultRouter()

router.register(r"users", UserViewSet)
router.register(r"telegram-users", TelegramUserViewSet)
router.register(r"branches", BranchViewSet)
router.register(r"regions", RegionViewSet)
router.register(r"districts", DistrictViewSet)

urlpatterns = [path("", include(router.urls))]
