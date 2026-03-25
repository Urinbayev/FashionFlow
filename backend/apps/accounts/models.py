"""
Account models: User, StyleProfile, Address.
"""

import uuid

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class UserManager(BaseUserManager):
    """Custom user manager supporting email-based authentication."""

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required.")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Custom user model using email for authentication."""

    GENDER_CHOICES = [
        ("M", "Male"),
        ("F", "Female"),
        ("NB", "Non-Binary"),
        ("NS", "Prefer not to say"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField("email address", unique=True, db_index=True)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, blank=True)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/", blank=True)
    is_influencer = models.BooleanField(default=False)
    influencer_code = models.CharField(max_length=50, blank=True, unique=True, null=True)
    influencer_commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    email_verified = models.BooleanField(default=False)
    marketing_consent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = "user"
        verbose_name_plural = "users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()


class StyleProfile(models.Model):
    """User style preferences for outfit recommendations."""

    STYLE_CHOICES = [
        ("casual", "Casual"),
        ("classic", "Classic"),
        ("bohemian", "Bohemian"),
        ("streetwear", "Streetwear"),
        ("minimalist", "Minimalist"),
        ("preppy", "Preppy"),
        ("athleisure", "Athleisure"),
        ("vintage", "Vintage"),
        ("glamorous", "Glamorous"),
        ("edgy", "Edgy"),
    ]

    FIT_CHOICES = [
        ("slim", "Slim Fit"),
        ("regular", "Regular Fit"),
        ("relaxed", "Relaxed Fit"),
        ("oversized", "Oversized"),
    ]

    BODY_TYPE_CHOICES = [
        ("hourglass", "Hourglass"),
        ("pear", "Pear"),
        ("apple", "Apple"),
        ("rectangle", "Rectangle"),
        ("inverted_triangle", "Inverted Triangle"),
        ("athletic", "Athletic"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="style_profile")
    preferred_styles = models.JSONField(default=list, blank=True, help_text="List of preferred style keys")
    preferred_fit = models.CharField(max_length=20, choices=FIT_CHOICES, blank=True)
    body_type = models.CharField(max_length=30, choices=BODY_TYPE_CHOICES, blank=True)
    preferred_colors = models.JSONField(default=list, blank=True, help_text="List of preferred color hex codes")
    avoided_colors = models.JSONField(default=list, blank=True)
    preferred_brands = models.JSONField(default=list, blank=True)
    budget_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    budget_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    height_cm = models.PositiveIntegerField(null=True, blank=True)
    weight_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    chest_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    waist_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    hip_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    shoe_size_eu = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    sustainability_preference = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "style profile"
        verbose_name_plural = "style profiles"

    def __str__(self):
        return f"Style Profile - {self.user.email}"


class Address(models.Model):
    """User shipping/billing addresses."""

    ADDRESS_TYPE_CHOICES = [
        ("shipping", "Shipping"),
        ("billing", "Billing"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    address_type = models.CharField(max_length=10, choices=ADDRESS_TYPE_CHOICES, default="shipping")
    full_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    street_address_1 = models.CharField(max_length=255)
    street_address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="US")
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "address"
        verbose_name_plural = "addresses"
        ordering = ["-is_default", "-created_at"]

    def __str__(self):
        return f"{self.full_name} - {self.street_address_1}, {self.city}"

    def save(self, *args, **kwargs):
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True,
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)
