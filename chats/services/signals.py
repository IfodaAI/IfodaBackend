from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chats.models import Message
from chats.services.telegram import send_telegram_message


@receiver(post_save, sender=Message)
def message_created_notify(sender, instance: Message, created, **kwargs):
    if not created:
        return

    # faqat USER yozgan xabar bo‘lsa
    if instance.role != "QUESTION":
        return

    channel_layer = get_channel_layer()

    # WebSocket notification
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "notify",
            "message": {"message": "Yangi bildirishnoma qabul qilindi!"},
        },
    )

    # Telegram notification
    TELEGRAM_CHAT_ID = "1330892088"  # admin yoki operator ID

    send_telegram_message(
        chat_id=TELEGRAM_CHAT_ID,
        text="🔔 Yangi savol keldi!"
    )
