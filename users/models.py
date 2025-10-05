from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from utils.models import BaseModel

from .managers import UserManager


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ("ADMIN", "Admin"),
        ("MANAGER", "Manager"),
        ("DISPATCHER", "Dispatcher"),
        ("USER", "User"),
    ]

    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="USER")
    telegram_id = models.BigIntegerField(unique=True, blank=True, null=True)
    phone_number = PhoneNumberField(unique=True)

    objects = UserManager()

    USERNAME_FIELD = "phone_number"

    # Serializer will return full_name property upon GET request, using this method will
    # let you to have this property without taking extra space in database.
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.first_name + self.last_name if self.first_name or self.last_name else self.phone_number}"


class TelegramUser(BaseModel):
    telegram_id = models.BigIntegerField(unique=True)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="telegram_user",
        blank=True,
        null=True,
    )
    username = models.CharField(max_length=32, blank=True, null=True, unique=True)
    first_name = models.CharField(max_length=64, blank=True, null=True)
    last_name = models.CharField(max_length=64, blank=True, null=True)
    region = models.ForeignKey("Region", on_delete=models.SET_NULL, blank=True, null=True)
    district = models.ForeignKey(
        "District", on_delete=models.SET_NULL, blank=True, null=True
    )
    phone_number = PhoneNumberField(unique=True, blank=True, null=True)

    def __str__(self):
        return self.username


class Branch(BaseModel):
    brainch_id = models.BigIntegerField(
        unique=True
    )  # This field is used to integrate with LOGIX system.
    manager = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="branches"
    )
    name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    phone_number = PhoneNumberField(unique=True)

    def __str__(self):
        return self.name

    class Meta:
        # Prevents model from being displayed as "Branchs" in admin panel
        verbose_name_plural = "Branches"


class Region(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    small_package = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class District(BaseModel):
    name = models.CharField(max_length=255)
    region = models.ForeignKey(
        Region, on_delete=models.CASCADE, related_name="districts"
    )
    small_package = models.BooleanField(default=False)

    def __str__(self):
        return self.name
