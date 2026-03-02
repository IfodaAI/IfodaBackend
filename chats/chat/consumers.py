import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from chats.models import Room, Message

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user is None or user.is_anonymous:
            await self.close()
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]

        # Room ownership tekshiruvi (IDOR himoya)
        has_access = await self.check_room_access(user, self.room_id)
        if not has_access:
            await self.close()
            return

        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
        except (json.JSONDecodeError, TypeError):
            await self.send(text_data=json.dumps({"error": "Noto'g'ri JSON format"}))
            return
        text = data.get("text")
        role = data.get("role", "QUESTION")
        content_type = data.get("content_type", "TEXT")
        sender = self.scope.get("user")

        message = await self.save_message(
            self.room_id, text, role, content_type, sender
        )

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat.message",
                "message": {
                    "id": str(message.id),
                    "text": message.text,
                    "role": message.role,
                    "content_type": message.content_type,
                    "status": message.status,
                    "sender": str(message.sender.id),
                    "created_date": message.created_date.isoformat(),
                },
            },
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event["message"]))

    @database_sync_to_async
    def check_room_access(self, user, room_id):
        """Room ownership tekshiruvi: ADMIN/superuser barcha roomlarga, USER faqat o'zinikilarga"""
        if user.is_superuser or getattr(user, "role", None) == "ADMIN":
            return Room.objects.filter(id=room_id).exists()
        return Room.objects.filter(id=room_id, owner=user).exists()

    @database_sync_to_async
    def save_message(self, room_id, text, role, content_type, sender):
        try:
            room = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            room = None
        if sender and getattr(sender, "role", None) == "USER":
            role = "QUESTION"
        else:
            role = "ANSWER"
        return Message.objects.create(
            room=room,
            text=text,
            role=role,
            content_type=content_type,
            sender=sender,
        )
    
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user is None or user.is_anonymous:
            await self.close()
            return

        self.group_name = "notifications"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def notify(self, event):
        message = event.get("message", True)
        await self.send(text_data=json.dumps({"message": message}))