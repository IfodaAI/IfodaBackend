# from rest_framework.viewsets import ModelViewSet
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.request import Request
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.decorators import action
# from django.db.models import Subquery, OuterRef, DateTimeField
# from django.http import HttpRequest
# from asgiref.sync import async_to_sync
# from channels.layers import get_channel_layer

# from .models import Room, Message
# from .serializer import RoomSerializer, MessageSerializer
# from .ai import generate_prompt
# from products.models import Disease
# from products.serializers import DiseaseSerializer

# class RoomViewSet(ModelViewSet):
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer
#     permission_classes=[IsAuthenticated]

#     def create(self, request:HttpRequest|Request, *args, **kwargs):
#         data=request.data.copy()
#         data["owner"]=request.user.id
#         serializer = self.get_serializer(data=data)
#         serializer.is_valid(raise_exception=True)
#         self.perform_create(serializer)
#         headers = self.get_success_headers(serializer.data)
#         return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
#     # def get_queryset(self):
#     #     user = self.request.user

#     #     # If user's role is admin, send all orders
#     #     if user.is_superuser or user.role == "ADMIN":
#     #         return Room.objects.all()

#     #     # If it's normal user, send only only their own orders.
#     #     return Room.objects.filter(owner=user)
#     def get_queryset(self):
#         user = self.request.user

#         last_message_sub = Message.objects.filter(
#             room=OuterRef("pk")
#         ).order_by("-created_date")

#         qs = Room.objects.annotate(
#             last_message_time=Subquery(
#                 last_message_sub.values("created_date")[:1],
#                 output_field=DateTimeField()
#             )
#         ).select_related("owner").order_by("-last_message_time")

#         if user.is_superuser or getattr(user, "role", None) == "ADMIN":
#             return qs

#         return qs.filter(owner=user)
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from django.db.models import Subquery, OuterRef, DateTimeField
from django.http import HttpRequest
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Room, Message
from .serializer import RoomSerializer, MessageSerializer
from .ai import generate_prompt
from products.models import Disease
from products.serializers import DiseaseSerializer


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request: HttpRequest | Request, *args, **kwargs):
        data = request.data.copy()
        data["owner"] = request.user.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def get_queryset(self):
        user = self.request.user

        # Subquery: oxirgi message vaqti
        last_message_sub = Message.objects.filter(
            room=OuterRef("pk")
        ).order_by("-created_date")

        # Roomlarni annotate qilamiz: last_message_time
        qs = Room.objects.annotate(
            last_message_time=Subquery(
                last_message_sub.values("created_date")[:1],
                output_field=DateTimeField()
            )
        ).select_related("owner").order_by(
            F('last_message_time').desc(nulls_last=True)  # NULL bo‘lsa oxiriga tushadi
        )

        # Admin barcha roomlarni ko‘radi
        if user.is_superuser or getattr(user, "role", None) == "ADMIN":
            return qs

        # Oddiy user faqat o‘zining roomlari
        return qs.filter(owner=user)

class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes=[IsAuthenticated]

    @action(detail=True, methods=["get"], url_path="ai_model_prediction")
    def ai_model_prediction(self, request, pk=None):
        message = self.get_object()
        # ✅ 1. Validatsiya: faqat IMAGE bo‘lishi kerak
        if message.content_type != "IMAGE" or not message.image:
            return Response(
                {
                    "error": "AI prediktsiya faqat rasm (IMAGE) content_type uchun ishlaydi.",
                    "content_type": message.content_type,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
                # ✅ 2. AI modelga yuborish (generate_prompt)
        try:
            result = generate_prompt(message.image.path)
        except Exception as e:
            return Response(
                {"error": f"AI model ishlov berishda xatolik: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        if result:
            disease=Disease.objects.filter(name__contains=result).first()
            serializer=DiseaseSerializer(disease)
            return Response(serializer.data)
            # # pill_ids listiga UUID lar string formatida saqlanadi
            # pill_ids = [str(uuid_obj) for uuid_obj in disease.pills.values_list('id', flat=True)]
            # return JsonResponse({
            #     'success': True,
            #     'pills': pill_ids,
            #     'diseases': [disease.id],  # Optional
            #     'order_id':order_id,
            #     "response":response
            # })
        return Response({}, status=status.HTTP_200_OK)

    def create(self, request: HttpRequest | Request, *args, **kwargs):
        data = request.data.copy()
        data["sender"] = request.user.id

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()

        channel_layer = get_channel_layer()
        room = message.room

        payload = {
            "id": str(message.id),
            "role": message.role,
            "sender": str(message.sender.id),
            "status": message.status,
            "content_type": message.content_type,
        }

        if message.content_type == "IMAGE":
            payload["image"] = request.build_absolute_uri(message.image.url) if message.image else ""
        elif message.content_type == "TEXT":
            payload["text"] = message.text
        elif message.content_type == "PRODUCT":
            payload["diseases"] = [{"name":d.name,"description":d.description} for d in message.diseases.all()]
            payload["products"] = [str(p.id) for p in message.products.all()]

        if room:
            async_to_sync(channel_layer.group_send)(
                f'chat_{room.id}',
                {"type": "chat_message", "message": payload},
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
"""
class TriggerNotification(APIView):
    def post(self, request):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "notifications", {"type": "notify", "message": {"message": "Yangi bildirishnoma qabul qilindi!"}}
        )
        return Response({"status": "sent"})
"""