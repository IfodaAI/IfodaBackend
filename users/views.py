from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny

from .models import User, TelegramUser, Branch
from .serializers import UserSerializer, TelegramUserSerializer, BranchSerializer

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TelegramUserViewSet(ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    permission_classes=[AllowAny]
    pagination_class=None
    filterset_fields=["telegram_id"]

class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer