from utils.serializers import BaseModelSerializer
from .models import Room, Message


class RoomSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Room


class MessageSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Message
