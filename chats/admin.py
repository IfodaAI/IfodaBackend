from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Topic, Message

@admin.register(Topic)
class TopicAdminClass(ModelAdmin):
    list_display = ["id", "name", "slug"]

@admin.register(Message)
class MessageAdminClass(ModelAdmin):
    list_display = ["sender", "text", "content_type", "topic", "status", "role"]