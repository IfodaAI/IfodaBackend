from django.urls import path, include

from rest_framework import routers

from .views import TopicViewSet, MessageViewSet

router = routers.DefaultRouter()

router.register(r"messages", MessageViewSet)
router.register(r"topics", TopicViewSet)

urlpatterns = [path("", include(router.urls))]
