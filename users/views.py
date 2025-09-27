from rest_framework.viewsets import ModelViewSet

from .models import User, TelegramUser, Branch
from .serializers import UserSerializer, TelegramUserSerializer, BranchSerializer

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TelegramUserViewSet(ModelViewSet):
    queryset = TelegramUser.objects.all()
    serializer_class = TelegramUserSerializer
    filterset_fields=["telegram_id"]

class BranchViewSet(ModelViewSet):
    queryset = Branch.objects.all()
    serializer_class = BranchSerializer