from rest_framework.serializers import ModelSerializer
from django.contrib.auth import get_user_model
from .models import TelegramUser, Branch

User = get_user_model()


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "telegram_id",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "role"
        )  # You cannot use __all__ because otherwise serializer will send user's password upon GET request as well.


class TelegramUserSerializer(ModelSerializer):
    class Meta:
        model = TelegramUser
        fields = "__all__"


class BranchSerializer(ModelSerializer):
    class Meta:
        model = Branch
        fields = "__all__"
