from rest_framework.viewsets import ModelViewSet

from .models import Room, Message
from .serializer import RoomSerializer, MessageSerializer


class RoomViewSet(ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
