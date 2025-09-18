from rest_framework.viewsets import ModelViewSet

from .models import Topic, Message
from .serializer import TopicSerializer, MessageSerializer


class TopicViewSet(ModelViewSet):
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
