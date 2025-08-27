from django.contrib import admin

from unfold.admin import ModelAdmin

from .models import Payment, Delivery


@admin.register(Payment)
class PaymentAdminClass(ModelAdmin):
    list_display = ["id", "order", "transaction_id", "amount", "status"]


@admin.register(Delivery)
class DeliveryAdminClass(ModelAdmin):
    list_display = ["id", "order", "tracking_number", "courier_name"]
