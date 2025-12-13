from django.contrib import admin
from django.contrib.auth.models import Group

from unfold.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin

from .models import User, TelegramUser, Branch, Region, District

admin.site.unregister(Group)

# @admin.register(User)
# class UserAdminClass(ModelAdmin):
#     list_display = [
#         "id",
#         "full_name",
#         "telegram_id",
#         "phone_number",
#         "role",
#         "is_staff",
#         "is_active",
#     ]

#     def full_name(self, obj):
#         return f"{obj.first_name} {obj.last_name}"
@admin.register(User)
class UserAdminClass(UserAdmin):
    model = User

    list_display = (
        "id",
        "full_name",
        "telegram_id",
        "phone_number",
        "role",
        "is_staff",
        "is_active",
    )

    search_fields = ("first_name", "last_name", "phone_number", "telegram_id")
    ordering = ("-id",)

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Shaxsiy ma'lumotlar", {
            "fields": (
                "first_name",
                "last_name",
                "telegram_id",
                "role",
            )
        }),
        ("Ruxsatlar", {
            "fields": (
                "is_active",
                "is_staff",
                "is_superuser",
                "groups",
                "user_permissions",
            )
        }),
        ("Muhim sanalar", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone_number",
                "password1",
                "password2",
                "is_staff",
                "is_active",
            ),
        }),
    )

    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    full_name.short_description = "To‘liq ism"

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