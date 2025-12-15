from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.db.models import Subquery, OuterRef, DateTimeField, F
from django.http import HttpRequest
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Room, Message
from .serializer import RoomSerializer, MessageSerializer

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

    def create(self, request: HttpRequest | Request, *args, **kwargs):
        # data = request.data.copy()
        # data["sender"] = request.user.id

        # serializer = self.get_serializer(data=data)
        # serializer.is_valid(raise_exception=True)
        # message = serializer.save()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # ❗ sender shu yerda beriladi
        message = serializer.save(sender=request.user)

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