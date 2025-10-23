from django.contrib import admin
from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin

from .models import User, TelegramUser, Branch, Region, District

admin.site.unregister(Group)

@admin.register(User)
class UserAdminClass(ModelAdmin):
    list_display = [
        "id",
        "full_name",
        "telegram_id",
        "phone_number",
        "role",
        "is_staff",
        "is_active",
    ]

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


@admin.register(TelegramUser)
class TelegramUserAdminClass(ModelAdmin):
    list_display = ["id", "full_name", "phone_number"]

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


@admin.register(Branch)
class BranchAdminClass(ModelAdmin):
    list_display = ["id", "name", "brainch_id", "location"]

    def location(self, obj):
        return f"{obj.latitude}° N {obj.longitude}° W"

@admin.register(Region)
class RegionAdminClass(ModelAdmin):
    list_display = ["id", "name"]

    
@admin.register(District)
class DistrictAdminClass(ModelAdmin):
    list_display = ["id", "name"]