from django.db import models

from utils.models import BaseModel
from users.models import TelegramUser
from products.models import ProductSKU


class Room(BaseModel):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Message(BaseModel):
    ROLE_CHOICES = [("QUESTION", "Question"), ("ANSWER", "Answer")]
    CONTENT_TYPE_CHOICES = [
        ("TEXT", "Text"),
        ("IMAGE", "Image"),
        ("PRODUCT", "Product"),
    ]
    STATUS_CHOICES = [
        ("UNREAD", "Unread"),
        ("NEW", "New"),
        ("UNREPLIED", "Unreplied"),
        ("REPLIED", "Replied"),
    ]

    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="messages", null=True, blank=True)
    content_type = models.CharField(choices=CONTENT_TYPE_CHOICES, default="TEXT")
    status = models.CharField(choices=STATUS_CHOICES, default="UNREAD")
    role = models.CharField(choices=ROLE_CHOICES, default="QUESTION")
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="messages/", blank=True, null=True)
    products = models.ManyToManyField(ProductSKU, related_name="messages", blank=True)
    sender = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name="messages",
        blank=True,
        null=True,
    )
