from django.contrib.auth import get_user_model
from .models import TelegramUser, Branch, Region, District
from utils.serializers import BaseModelSerializer
from rest_framework import serializers

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
            "created_date",
            "state"
        )  # You cannot use __all__ because otherwise serializer will send user's password upon GET request as well.


class UserRegisterSerializer(BaseModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = [
            "id",
            "first_name",
            "last_name",
            "phone_number",
            "telegram_id",
            "password",
        ]

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # parolni hash qiladi
        user.save()
        return user


class TelegramUserSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = TelegramUser


class BranchSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Branch


class RegionSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Region


class DistrictSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = District
