from utils.serializers import BaseModelSerializer
from .models import Topic, Message


class TopicSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Topic


class MessageSerializer(BaseModelSerializer):
    class Meta(BaseModelSerializer.Meta):
        model = Message
