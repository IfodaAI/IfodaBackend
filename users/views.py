from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import AnonRateThrottle
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from rest_framework.views import APIView
from django.http import HttpRequest
from rest_framework_simplejwt.tokens import RefreshToken


class AuthRateThrottle(AnonRateThrottle):
    rate = "60/hour"

from .permissions import PostAndCheckUserOnly
from .models import User, TelegramUser, Branch, Region, District
from .serializers import (
    UserSerializer,
    TelegramUserSerializer,
    TelegramWebAppAuthSerializer,
    BranchSerializer,
    RegionSerializer,
    DistrictSerializer,
)
from .telegram_validator import TelegramInitDataValidator
from utils.utils import get_distance_from_lat_lon_in_km
from utils.permissions import IsAdminOrReadOnly


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=[PostAndCheckUserOnly]


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
    permission_classes = [IsAdminOrReadOnly]

    @action(detail=False, methods=["get"])
    def get_nearest_branches(self, request: HttpRequest | Request):
        try:
            user_lat = float(request.GET.get("latitude"))
            user_lon = float(request.GET.get("longitude"))
        except (TypeError, ValueError):
            return Response(
                {"error": "latitude va longitude query param sifatida yuborilishi kerak"},
                status=400,
            )

        # Faqat kerakli maydonlarni olish (optimizatsiya)
        branch_data = Branch.objects.values("id", "name", "phone_number", "latitude", "longitude")

        branches = [
            {
                "id": branch["id"],
                "name": branch["name"],
                "phone_number": str(branch["phone_number"]),
                "latitude": branch["latitude"],
                "longitude": branch["longitude"],
                "distance": round(
                    get_distance_from_lat_lon_in_km(
                        user_lat, user_lon, branch["latitude"], branch["longitude"]
                    ),
                    2,
                ),
            }
            for branch in branch_data
        ]

        # Masofaga qarab saralash va 5 ta eng yaqinini olish
        nearest = sorted(branches, key=lambda x: x["distance"])[:5]
        return Response(nearest)

class RegionViewSet(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer
    permission_classes = [IsAdminOrReadOnly]

class DistrictViewSet(ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields=["region"]


class TelegramWebAppAuthView(APIView):
    """
    POST /api/auth/telegram/
    Body: { "init_data": "<raw initData string from Telegram.WebApp.initData>" }
    Returns: { "access_token", "refresh_token", "user", "is_new_user" }

    Faqat role="USER" bo'lgan foydalanuvchilar uchun ishlaydi.
    """
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = TelegramWebAppAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        init_data = serializer.validated_data["init_data"]

        validator = TelegramInitDataValidator()
        try:
            validated_data = validator.validate(init_data)
        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        tg_user = validated_data.get("user", {})
        telegram_id = tg_user.get("id")

        if not telegram_id:
            return Response(
                {"error": "User data not found in initData"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # TelegramUser ni yangilash yoki yaratish
        tg_user_obj, _ = TelegramUser.objects.update_or_create(
            telegram_id=telegram_id,
            defaults={
                "first_name": tg_user.get("first_name", ""),
                "last_name": tg_user.get("last_name", ""),
                "username": tg_user.get("username", ""),
                "photo_url": tg_user.get("photo_url", ""),
                "language_code": tg_user.get("language_code", ""),
            },
        )

        # User ni telegram_id orqali topish
        user = User.objects.filter(telegram_id=telegram_id).first()
        is_new_user = False

        if user:
            # Mavjud user — faqat USER rolida bo'lsa ruxsat berish
            if user.role != "USER":
                return Response(
                    {"error": "Bu auth faqat USER roli uchun."},
                    status=status.HTTP_403_FORBIDDEN,
                )
        else:
            # Yangi user yaratish — TelegramUser da phone_number bo'lishi kerak
            if tg_user_obj.phone_number:
                user = User.objects.create_user(
                    phone_number=str(tg_user_obj.phone_number),
                    telegram_id=telegram_id,
                    first_name=tg_user.get("first_name", ""),
                    role="USER",
                )
                is_new_user = True
            else:
                return Response(
                    {
                        "error": "Phone number not found. Please register via Telegram bot first.",
                        "telegram_user": TelegramUserSerializer(tg_user_obj).data,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # TelegramUser ni User bilan bog'lash (agar bog'lanmagan bo'lsa)
        if not tg_user_obj.user:
            tg_user_obj.user = user
            tg_user_obj.save(update_fields=["user"])

        # User ma'lumotlarini yangilash
        updated_fields = []
        if tg_user.get("first_name") and not user.first_name:
            user.first_name = tg_user["first_name"]
            updated_fields.append("first_name")
        if tg_user.get("last_name") and not user.last_name:
            user.last_name = tg_user["last_name"]
            updated_fields.append("last_name")
        if updated_fields:
            user.save(update_fields=updated_fields)

        # JWT token berish
        refresh = RefreshToken.for_user(user)

        return Response({
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
            "user": {
                "id": str(user.id),
                "telegram_id": user.telegram_id,
                "phone_number": str(user.phone_number),
                "first_name": user.first_name,
                "last_name": user.last_name,
                "full_name": user.full_name,
                "role": user.role,
            },
            "is_new_user": is_new_user,
        })


class MeView(APIView):
    """GET /api/auth/me/ — JWT bilan himoyalangan"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": str(user.id),
            "telegram_id": user.telegram_id,
            "phone_number": str(user.phone_number),
            "first_name": user.first_name,
            "last_name": user.last_name,
            "full_name": user.full_name,
            "role": user.role,
            "is_active": user.is_active,
        }
        # TelegramUser ma'lumotlarini qo'shish
        tg_user = TelegramUser.objects.filter(telegram_id=user.telegram_id).first()
        if tg_user:
            data["photo_url"] = tg_user.photo_url
            data["language_code"] = tg_user.language_code
            data["username"] = tg_user.username
        return Response(data)
