from django.db import models

from phonenumber_field.modelfields import PhoneNumberField

from users.models import User, Branch
from products.models import ProductSKU
from utils.models import BaseModel


class Order(BaseModel):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PROCESSING", "Processing"),
        ("IN_PAYMENT", "In payment"),
        ("COMPLETED", "Completed"),
        ("REJECTED", "Rejected"),
    ]
    DELIVERY_METHOD_CHOICES = [("DELIVERY", "Delivery"), ("PICK_UP", "Pick Up")]

    amount = models.FloatField(blank=True,null=True)
    status = models.CharField(choices=STATUS_CHOICES, default="PENDING")
    branch = models.ForeignKey(
        Branch, on_delete=models.SET_NULL, blank=True, null=True, related_name="orders"
    )
    shipping_address = models.CharField(max_length=50, blank=True, null=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    delivery_method = models.CharField(
        choices=DELIVERY_METHOD_CHOICES, default="DELIVERY"
    )
    delivery_price = models.FloatField(default=0)
    delivery_latitude = models.CharField(max_length=50)
    delivery_longitude = models.CharField(max_length=50)
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="orders",
    )

    def __str__(self):
        return f"Order {self.id}"


class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="order_items"
    )
    product = models.ForeignKey(
        ProductSKU, on_delete=models.CASCADE, related_name="order_items"
    )
    quantity = models.BigIntegerField(default=1)
    price = models.FloatField()

    def save(self):
        self.price = self.product.price * self.quantity
        print("\n\n\nin model",self.price)
        return super().save()

    def __str__(self):
        return f"OrderItem {self.id} of Order {self.order.id}"