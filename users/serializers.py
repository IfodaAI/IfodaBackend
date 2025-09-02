from django.contrib.auth import get_user_model
from .models import TelegramUser, Branch
from utils.serializers import BaseModelSerializer

User = get_user_model()


class UserSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = User
        fields = (
            "telegram_id",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "role",
        )  # You cannot use __all__ because otherwise serializer will send user's password upon GET request as well.


class TelegramUserSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = TelegramUser


class BranchSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Branch
