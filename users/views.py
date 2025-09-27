from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.http import HttpRequest
from .permissions import PostAndCheckUserOnly

from .models import User, TelegramUser, Branch
from .serializers import UserSerializer, TelegramUserSerializer, BranchSerializer, UserRegisterSerializer

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=[PostAndCheckUserOnly]

    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                {"id": user.id, "full_name": user.full_name},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        instance=queryset.filter(telegram_id=telegram_id).last()
        if not instance:
            return Response({})
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer