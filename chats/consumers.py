import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Room, Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if user is None or user.is_anonymous:
            await self.close()
            return

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name, self.channel_name
            )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
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