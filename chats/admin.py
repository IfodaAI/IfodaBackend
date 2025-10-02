from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Room, Message

@admin.register(Room)
class RoomAdminClass(ModelAdmin):
    list_display = ["id", "name"]

@admin.register(Message)
class MessageAdminClass(ModelAdmin):
    list_display = ["sender", "text", "content_type", "room", "status", "role"]