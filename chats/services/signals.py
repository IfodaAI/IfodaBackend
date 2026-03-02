from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from chats.models import Message
from chats.services.telegram import send_telegram_message,send_telegram_message_with_button


@receiver(post_save, sender=Message)
def message_created_notify(sender, instance: Message, created, **kwargs):
    if not created:
        return

    # faqat USER yozgan xabar bo’lsa
    if instance.role != "QUESTION":
        send_telegram_message_with_button(
            chat_id=instance.room.owner.telegram_id,
            text="🔔 Yangi bildirishnoma qabul qilindi!",
            button_text="Bildiruvnomaning batafsil ko’rinishi",
            webapp_url=f"{settings.WEBAPP_URL}/chat/{instance.room.id}"
        )
        return

    channel_layer = get_channel_layer()

    # WebSocket notification
    async_to_sync(channel_layer.group_send)(
        "notifications",
        {
            "type": "notify",
            "message": "Yangi bildirishnoma qabul qilindi!",
        },
    )

    # Telegram notification
    send_telegram_message(
        chat_id=settings.TELEGRAM_ADMIN_CHAT_ID,
        text="🔔 Yangi bildirishnoma qabul qilindi!\n"\
             f"https://admin.ifoda-shop.uz/chats/{instance.room.id}"
    )
