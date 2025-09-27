from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from django.http import HttpRequest
from .permissions import PostAndCheckUserOnly

from .models import User, TelegramUser, Branch
from .serializers import UserSerializer, TelegramUserSerializer, BranchSerializer

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TelegramUserViewSet(ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes=[PostAndCheckUserOnly]
    
    @action(detail=False, methods=["get"])
    def check_user(self, request:HttpRequest|Request):
        telegram_id=request.GET.get("telegram_id")
        if not telegram_id:
            raise ValidationError({"telegram_id": "Bu maydon majburiy."})
        queryset = self.filter_queryset(self.get_queryset())
        instance=queryset.filter(telegram_id=telegram_id)
        if not instance:
            return Response({})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer