from django.contrib.auth import get_user_model
from .models import TelegramUser, Branch, Region, District
from utils.serializers import BaseModelSerializer
from rest_framework import serializers

User = get_user_model()

class UserSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = User
        fields = (
            "id",
            "telegram_id",
            "phone_number",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "created_date",
            "state"
        )  # You cannot use __all__ because otherwise serializer will send user's password upon GET request as well.

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get("request")
        if (
            request
            and request.method == "GET"
            and request.query_params.get("telegram_user") == "true"
        ):
            telegram_user = getattr(instance, "telegram_user", None)
            if telegram_user:
                data["telegram_user"] = TelegramUserSerializer(telegram_user).data
            else:
                data["telegram_user"] = None
        return data

class TelegramWebAppAuthSerializer(serializers.Serializer):
    init_data = serializers.CharField(required=True)


class TelegramUserSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = TelegramUser
        fields = (
            "id",
            "telegram_id",
            "user",
            "username",
            "first_name",
            "last_name",
            "photo_url",
            "language_code",
            "region",
            "district",
            "phone_number",
            "created_date",
        )


class BranchSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Branch
        fields = (
            "id",
            "branch_id",
            "manager",
            "name",
            "latitude",
            "longitude",
            "phone_number",
        )


class RegionSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Region
        fields = ("id", "name", "small_package")


class DistrictSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = District
        fields = ("id", "name", "region", "small_package")

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        data["user"] = {
            "id": str(user.id),
            "phone_number": str(user.phone_number),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role,
            "is_staff": user.is_staff,
            "telegram_id": user.telegram_id,
        }

        return data
