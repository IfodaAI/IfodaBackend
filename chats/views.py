from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from rest_framework.permissions import IsAuthenticated
from django.http import HttpRequest
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from .models import Room, Message
from .serializer import RoomSerializer, MessageSerializer

class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes=[IsAuthenticated]

    def create(self, request:HttpRequest|Request, *args, **kwargs):
        data=request.data
        data["owner"]=request.user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def get_queryset(self):
        user = self.request.user

        # If user's role is admin, send all orders
        if user.is_superuser or user.role == "ADMIN":
            return Room.objects.all()

        # If it's normal user, send only only their own orders.
        return Room.objects.filter(owner=user)

class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes=[IsAuthenticated]

    # def create(self, request:HttpRequest|Request, *args, **kwargs):
    #     data = request.data.copy()
    #     data["sender"]=request.user.id
    #     serializer = self.get_serializer(data=data)
    #     if serializer.is_valid():
    #         message = serializer.save()
    #         channel_layer = get_channel_layer()
    #         room_id = message.room.id
    #         data={
    #                 "id": str(message.id),
    #                 "role": message.role,
    #                 "sender": str(message.sender.id),
    #                 "status": message.status,
    #                 "content_type":message.content_type,
    #                 # "image": request.build_absolute_uri(message.image.url) if message.image else "",
    #                 # "text":message.text,
    #         }
    #         if message.content_type=="IMAGE":
    #             data["image"]=request.build_absolute_uri(message.image.url) if message.image else ""
    #         elif message.content_type=="TEXT":
    #             data["text"]=message.text
    #         else:
    #             data["diseases"]=[disease.name for disease in message.diseases.all()]
    #             data["products"]=[product.id for product in message.products.all()]
    #         async_to_sync(channel_layer.group_send)(
    #             f'chat_{room_id}',
    #             {
    #                 "type": "chat_message",
    #                 "message": data
    #             },
    #         )
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
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
            payload["diseases"] = [d.name for d in message.diseases.all()]
            payload["products"] = [p.id for p in message.products.all()]

        if room:
            async_to_sync(channel_layer.group_send)(
                f'chat_{room.id}',
                {"type": "chat_message", "message": payload},
            )

        return Response(serializer.data, status=status.HTTP_201_CREATED)
