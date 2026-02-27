from utils.serializers import BaseModelSerializer
from .models import Room, Message
from django.http import HttpRequest
from users.serializers import UserSerializer
from rest_framework.serializers import SerializerMethodField

class RoomSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Room
        fields = ("id", "name", "owner", "created_date", "updated_date")

    def __init__(self, *args, **kwargs):
        super(RoomSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")
        if request and request.method == "GET":
            messages = request.GET.get("messages")
            if messages == "true":
                self.fields["messages"] = MessageSerializer(context=self.context, many=True)
            owner = request.GET.get("owner")
            if owner == "true":
                self.fields["owner"] = UserSerializer(context=self.context)


class MessageSerializer(BaseModelSerializer):
    diseases_info = SerializerMethodField(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Message
        fields = (
            "id",
            "room",
            "content_type",
            "status",
            "role",
            "text",
            "image",
            "diseases",
            "diseases_info",
            "products",
            "sender",
            "created_date",
            "updated_date",
        )
        read_only_fields = ("id", "diseases_info", "created_date", "updated_date")

    def get_diseases_info(self, obj):
        return list(obj.diseases.values("name", "description"))