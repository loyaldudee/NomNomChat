import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.contrib.auth.base_user import BaseUserManager  # 👈 Added import

# ✅ New Custom Manager
class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email_hash is the unique identifier
    instead of username.
    """
    def create_user(self, email_hash, password=None, **extra_fields):
        if not email_hash:
            raise ValueError("The Email Hash must be set")
        user = self.model(email_hash=email_hash, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email_hash, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        # Fix for fields that might be required by your specific logic
        # Since your User model has year/branch as mandatory, we must provide defaults for superuser
        extra_fields.setdefault("year", 0) 
        extra_fields.setdefault("branch", "Admin")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email_hash, password, **extra_fields)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Disable default username/email (we use OTP)
    username = None
    email = None

    email_hash = models.CharField(max_length=64, unique=True)

    internal_username = models.CharField(
        max_length=30,
        unique=True,
        null=True,
        blank=True
    )

    year = models.IntegerField()
    branch = models.CharField(max_length=50)
    is_banned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = "email_hash"
    REQUIRED_FIELDS = []  # No other fields prompted (year/branch handled in manager default)

    # 👇 Link the custom manager here
    objects = CustomUserManager()

    def __str__(self):
        return str(self.id)


class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    attempts = models.IntegerField(default=0)

    def is_expired(self):
        return timezone.now() > self.expires_at