from django.contrib.auth.models import BaseUserManager
from utils.utils import normalize_phone
import random,string

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError("Entering a phone number is required.")
        phone_number = normalize_phone(phone_number)
        extra_fields.setdefault("is_active", True)
        user = self.model(phone_number=phone_number, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("role", "ADMIN")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("role") != "ADMIN":
            raise ValueError("In order to create superuser your role must be ADMIN.")
        return self.create_user(phone_number, password, **extra_fields)
    
    def generate_random_password(self, length=10):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))

    def create_user_with_random_password(self, phone_number, telegram_id, first_name=""):
        if not phone_number:
            raise ValueError("Phone number is required")

        password = self.generate_random_password()

        user = self.model(
            phone_number=phone_number,
            telegram_id=telegram_id,
            first_name=first_name,
            role="USER",
            is_active=True
        )

        user.set_password(password)
        user.save(using=self._db)

        return user
