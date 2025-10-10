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

    def create(self, request:HttpRequest|Request, *args, **kwargs):
        data=request.data
        data["sender"]=request.user.id
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            message = serializer.save()
            channel_layer = get_channel_layer()
            room_id = message.room.id
            async_to_sync(channel_layer.group_send)(
                f'chat_{room_id}',
                {
                    "type": "chat_message",
                    "message": {
                        "id": str(message.id),
                        "role": message.role,
                        "sender": str(message.sender.id),
                        "status": message.status,
                        "content_type":message.content_type,
                        "image": request.build_absolute_uri(message.image.url) if message.image else "",
                        "text":message.text,
                    }
                },
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
