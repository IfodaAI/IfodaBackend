from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdminClass(ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "branch",
        "total_price",
        "delivery_method",
        "delivery_price",
    ]


@admin.register(OrderItem)
class OrderItemAdminClass(ModelAdmin):
    list_display = ["id", "order", "quantity", "price"]
