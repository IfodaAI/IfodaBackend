from utils.serializers import BaseModelSerializer
from .models import Room, Message
from django.http import HttpRequest

class RoomSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Room
        depth=1

    def __init__(self, *args, **kwargs):
        super(RoomSerializer, self).__init__(*args, **kwargs)
        request: HttpRequest = self.context.get("request")
        if request and request.method == "GET":
            messages = request.GET.get("messages")
            if messages == "true":
                self.fields["messages"] = MessageSerializer(context=self.context,many=True)

class MessageSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Message
