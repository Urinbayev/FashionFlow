"""
Promotion models: Promotion, Coupon, FlashSale.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Promotion(models.Model):
    """General promotion campaigns."""

    PROMO_TYPE_CHOICES = [
        ("percentage", "Percentage Discount"),
        ("fixed", "Fixed Amount Discount"),
        ("bogo", "Buy One Get One"),
        ("free_shipping", "Free Shipping"),
        ("bundle", "Bundle Deal"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    promo_type = models.CharField(max_length=20, choices=PROMO_TYPE_CHOICES)
    discount_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        help_text="Percentage (0-100) for percentage type, or fixed amount.",
    )
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        help_text="Cap on the discount amount for percentage promotions.",
    )
    applicable_categories = models.ManyToManyField(
        "products.Category", blank=True, related_name="promotions",
    )
    applicable_products = models.ManyToManyField(
        "products.Product", blank=True, related_name="promotions",
    )
    applicable_collections = models.ManyToManyField(
        "products.Collection", blank=True, related_name="promotions",
    )
    banner_image = models.ImageField(upload_to="promotions/banners/", blank=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.name} ({self.get_promo_type_display()})"

    @property
    def is_currently_active(self):
        now = timezone.now()
        return self.is_active and self.start_date <= now <= self.end_date


class Coupon(models.Model):
    """Redeemable coupon code."""

    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage"),
        ("fixed", "Fixed Amount"),
        ("free_shipping", "Free Shipping"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True, db_index=True)
    description = models.CharField(max_length=300, blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    max_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    max_uses = models.PositiveIntegerField(default=0, help_text="0 = unlimited")
    max_uses_per_user = models.PositiveIntegerField(default=1)
    current_uses = models.PositiveIntegerField(default=0)
    applicable_categories = models.ManyToManyField("products.Category", blank=True)
    applicable_products = models.ManyToManyField("products.Product", blank=True)

    # Influencer association
    influencer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="influencer_coupons",
        limit_choices_to={"is_influencer": True},
    )

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()} - {self.discount_value})"

    @property
    def is_valid(self):
        now = timezone.now()
        if not self.is_active:
            return False
        if now < self.start_date or now > self.end_date:
            return False
        if self.max_uses > 0 and self.current_uses >= self.max_uses:
            return False
        return True

    def calculate_discount(self, subtotal):
        if not self.is_valid:
            return 0
        if subtotal < self.min_purchase_amount:
            return 0
        if self.discount_type == "percentage":
            discount = subtotal * (self.discount_value / 100)
            if self.max_discount_amount:
                discount = min(discount, self.max_discount_amount)
            return round(discount, 2)
        elif self.discount_type == "fixed":
            return min(self.discount_value, subtotal)
        elif self.discount_type == "free_shipping":
            return 0  # Handled separately in order logic
        return 0


class CouponUsage(models.Model):
    """Tracks individual coupon usage."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="coupon_usages")
    order = models.ForeignKey("orders.Order", on_delete=models.SET_NULL, null=True, related_name="coupon_usage")
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2)
    used_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-used_at"]

    def __str__(self):
        return f"{self.user.email} used {self.coupon.code}"


class FlashSale(models.Model):
    """Time-limited flash sale with deep discounts."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    products = models.ManyToManyField("products.Product", related_name="flash_sales")
    discount_percentage = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(90)],
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    banner_image = models.ImageField(upload_to="flash_sales/", blank=True)
    is_active = models.BooleanField(default=True)
    max_quantity_per_user = models.PositiveIntegerField(default=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-start_time"]

    def __str__(self):
        return f"{self.name} ({self.discount_percentage}% off)"

    @property
    def is_live(self):
        now = timezone.now()
        return self.is_active and self.start_time <= now <= self.end_time

    @property
    def time_remaining_seconds(self):
        if not self.is_live:
            return 0
        remaining = self.end_time - timezone.now()
        return max(0, int(remaining.total_seconds()))
