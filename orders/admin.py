from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import Order, OrderItem, Delivery



@admin.register(Delivery)
class DeliveryAdminClass(ModelAdmin):
    list_display = ["id", "order", "tracking_number", "courier_name"]


@admin.register(Order)
class OrderAdminClass(ModelAdmin):
    list_display = [
        "id",
        "user",
        "status",
        "branch",
        "amount",
        "delivery_method",
        "delivery_price",
    ]


@admin.register(OrderItem)
class OrderItemAdminClass(ModelAdmin):
    list_display = ["id", "order", "quantity", "price"]
