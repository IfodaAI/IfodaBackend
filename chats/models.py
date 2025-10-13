from django.db import models
from django.contrib.auth import get_user_model

from utils.models import BaseModel
from products.models import Disease,ProductSKU

User = get_user_model()


class Room(BaseModel):
    name = models.CharField(max_length=50)
    owner = models.ForeignKey(
        User,
        related_name="rooms",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

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

    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="messages", null=True, blank=True
    )
    content_type = models.CharField(choices=CONTENT_TYPE_CHOICES, default="TEXT")
    status = models.CharField(choices=STATUS_CHOICES, default="UNREAD")
    role = models.CharField(choices=ROLE_CHOICES, default="QUESTION")
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="messages/", blank=True, null=True)
    diseases = models.ManyToManyField(Disease, related_name="messages", blank=True)
    products = models.ManyToManyField(ProductSKU, related_name="messages", blank=True)
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="messages",
        blank=True,
        null=True,
    )

    def save(self, force_insert = ..., force_update = ..., using = ..., update_fields = ...):
        if self.sender and getattr(self.sender, "role", None) == "USER":
            self.role = "QUESTION"
        else:
            self.role = "ANSWER"
        return super().save(force_insert, force_update, using, update_fields)
