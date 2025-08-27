from rest_framework.serializers import ModelSerializer
from .models import Topic, Message

class TopicSerializer(ModelSerializer):
    class Meta:
        model = Topic
        fields = "__all__"


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = "__all__"