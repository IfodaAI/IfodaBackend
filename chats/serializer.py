from utils.serializers import BaseModelSerializer
from .models import Room, Message
from django.http import HttpRequest
from users.serializers import UserSerializer
from rest_framework.serializers import SerializerMethodField

class RoomSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Room
        # depth=1

    def __init__(self, *args, **kwargs):
        super(RoomSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")
        if request and request.method == "GET":
            messages = request.GET.get("messages")
            if messages == "true":
                self.fields["messages"] = MessageSerializer(context=self.context,many=True)
            owner = request.GET.get("owner")
            if owner == "true":
                self.fields["owner"] = UserSerializer(context=self.context)

class MessageSerializer(BaseModelSerializer):
    diseases_info = SerializerMethodField(read_only=True)

    class Meta(BaseModelSerializer.Meta):
        model = Message
        read_only_fields = ["diseases_info"]
    
    def get_diseases_info(self, obj):
        # Disease modelida name va description maydonlari mavjud deb faraz qilamiz
        return list(obj.diseases.values("name", "description"))