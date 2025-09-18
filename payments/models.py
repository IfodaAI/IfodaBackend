from django.db import models
from utils.models import BaseModel
from orders.models import Order


class Payment(BaseModel):
    PAYMENT_METHODS = [
        ("PAYME", "PayMe"),
        ("CLICK", "Click"),
        ("CASH", "Cash"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("SUCCESS", "Success"),
        ("FAILED", "Failed"),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(choices=PAYMENT_METHODS)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    status = models.CharField(choices=STATUS_CHOICES, default="PENDING")
    transaction_id = models.CharField(
        max_length=255, null=True, blank=True
    )  # gateway ID

    def __str__(self):
        return f"Payment {self.id}"


class Delivery(BaseModel):
    STATUS_CHOICES = [
        ("RECEIVED", "Received"),
        ("PROCESSING", "Processing"),
        ("IN_TRANSIT", "In Transit"),
        ("OUT_FOR_DELIVERY", "Out For Delivery"),
        ("DELIVERED", "Delivered"),
        ("REJECTED", "Rejected"),
    ]

    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="delivery"
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="RECEIVED")
    tracking_number = models.CharField(max_length=100, null=True, blank=True)
    courier_name = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return f"Delivery for Order {self.order.id}"

    class Meta:
        verbose_name_plural = "Deliveries"
