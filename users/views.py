from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from django.http import HttpRequest
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import PostAndCheckUserOnly

from .models import User, PasswordResetCode, TelegramUser, Branch, Region, District
from .serializers import UserSerializer, TelegramUserSerializer, BranchSerializer, UserRegisterSerializer, RegionSerializer, DistrictSerializer
from utils.utils import get_distance_from_lat_lon_in_km
from chats.services.telegram import send_telegram_message_with_button,delete_telegram_message
from django.contrib.auth.hashers import make_password

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes=[PostAndCheckUserOnly]

    @action(detail=False, methods=["get"], permission_classes=[AllowAny])
    def get_token(self, request):
        phone_number = request.GET.get("phone_number")
        if not phone_number:
            instance=self.get_queryset().filter(phone_number=phone_number).last()
            refresh = RefreshToken.for_user(instance)
            return Response(
                {
                    "id": instance.id,
                    "full_name": instance.full_name,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED
            )
        user = User.objects.create_user_with_random_password(phone_number)
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "id": user.id,
                "full_name": user.full_name,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            },
            status=status.HTTP_201_CREATED
        )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["post"])
    def register(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response(
                {
                    "id": user.id,
                    "full_name": user.full_name,
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["POST"], url_path="get-verification-code",permission_classes=[PostAndCheckUserOnly])
    def get_verification_code(self, request):
        phone = request.data.get("phone_number")

        if not phone:
            return Response(
                {"detail": "phone_number majburiy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "Foydalanuvchi topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        if not user.telegram_id:
            return Response(
                {"detail": "User telegram bilan bog‘lanmagan"},
                status=status.HTTP_400_BAD_REQUEST
            )

        code = PasswordResetCode.generate_code()

        prc=PasswordResetCode.objects.create(
            user=user,
            code=code,
            expires_at=timezone.now() + timedelta(minutes=5)
        )

        # send_telegram_message(
        #     chat_id=user.telegram_id,
        #     text=f"🔐 Tasdiqlash kodi: <code>{code}</code>\n\nKod 5 daqiqa amal qiladi."
        # )

        msg_id = send_telegram_message_with_button(
            chat_id=user.telegram_id,
            text=f"🔐 Tasdiqlash kodi: <code>{code}</code>\n\nKod 5 daqiqa amal qiladi.",
            button_text="➡️ Parol yangilash sahifasiga o‘tish",
            webapp_url=f"https://ifoda-market.netlify.app/reset-psw?code={str(code)}&phone_number={phone}",
        )
        prc.message_id=msg_id
        prc.save()

        return Response(
            {"detail": "Verification kodi telegramga yuborildi"},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=["post"], url_path="reset-password")
    def reset_password(self, request):
        phone = request.data.get("phone_number")
        code = request.data.get("code")
        new_password = request.data.get("new_password")

        if not all([phone, code, new_password]):
            return Response(
                {"detail": "Barcha fieldlar majburiy"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(phone_number=phone)
        except User.DoesNotExist:
            return Response(
                {"detail": "User topilmadi"},
                status=status.HTTP_404_NOT_FOUND
            )

        reset_code = (
            PasswordResetCode.objects
            .filter(user=user, code=code, is_used=False)
            .order_by("-created_at")
            .first()
        )

        if not reset_code:
            return Response(
                {"detail": "Kod noto‘g‘ri"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if reset_code.is_expired():
            return Response(
                {"detail": "Kod eskirgan"},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.password = make_password(new_password)
        user.save(update_fields=["password"])

        reset_code.is_used = True
        if reset_code.message_id:
            delete_telegram_message(user.telegram_id, reset_code.message_id)
        reset_code.save(update_fields=["is_used"])

        return Response(
            {"detail": "Parol muvaffaqiyatli o‘zgartirildi"},
            status=status.HTTP_200_OK
        )

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

        branches = []
        for branch in Branch.objects.all():
            distance = get_distance_from_lat_lon_in_km(
                user_lat, user_lon, branch.latitude, branch.longitude
            )
            branches.append({
                "id": branch.id,
                "name": branch.name,
                "phone_number": str(branch.phone_number),
                "latitude": branch.latitude,
                "longitude": branch.longitude,
                "distance": round(distance, 2),
            })

        # Masofaga qarab saralash va 10 ta eng yaqinini olish
        nearest = sorted(branches, key=lambda x: x["distance"])[:5]
        return Response(nearest)

class RegionViewSet(ModelViewSet):
    queryset = Region.objects.all()
    serializer_class = RegionSerializer

class DistrictViewSet(ModelViewSet):
    queryset = District.objects.all()
    serializer_class = DistrictSerializer
    filterset_fields=["region"]
