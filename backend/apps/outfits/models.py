"""
Outfit models: Outfit, OutfitItem, StyleBoard.
"""

import uuid

from django.conf import settings
from django.db import models


class Outfit(models.Model):
    """An outfit composed of multiple products."""

    OCCASION_CHOICES = [
        ("casual", "Casual"),
        ("work", "Work / Office"),
        ("formal", "Formal / Evening"),
        ("date_night", "Date Night"),
        ("weekend", "Weekend"),
        ("vacation", "Vacation"),
        ("athleisure", "Athleisure"),
        ("streetwear", "Streetwear"),
    ]

    SEASON_CHOICES = [
        ("spring", "Spring"),
        ("summer", "Summer"),
        ("fall", "Fall"),
        ("winter", "Winter"),
        ("all_season", "All Season"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="outfits")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    occasion = models.CharField(max_length=20, choices=OCCASION_CHOICES, blank=True)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES, default="all_season")
    cover_image = models.ImageField(upload_to="outfits/covers/", blank=True)
    is_public = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    likes_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="liked_outfits"
    )
    tags = models.JSONField(default=list, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} by {self.user.email}"

    def calculate_total_price(self):
        self.total_price = sum(
            item.product.current_price for item in self.items.select_related("product")
        )
        self.save(update_fields=["total_price"])


class OutfitItem(models.Model):
    """A product within an outfit, positioned in a specific slot."""

    SLOT_CHOICES = [
        ("top", "Top"),
        ("bottom", "Bottom"),
        ("outerwear", "Outerwear"),
        ("dress", "Dress / One-piece"),
        ("shoes", "Shoes"),
        ("bag", "Bag"),
        ("accessory_1", "Accessory 1"),
        ("accessory_2", "Accessory 2"),
        ("accessory_3", "Accessory 3"),
        ("hat", "Hat"),
        ("jewelry", "Jewelry"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    outfit = models.ForeignKey(Outfit, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="outfit_items")
    slot = models.CharField(max_length=20, choices=SLOT_CHOICES)
    notes = models.CharField(max_length=500, blank=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order"]
        unique_together = ["outfit", "slot"]

    def __str__(self):
        return f"{self.get_slot_display()}: {self.product.name}"


class StyleBoard(models.Model):
    """Pinterest-style board for saving and organizing outfits."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="style_boards")
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="boards/covers/", blank=True)
    outfits = models.ManyToManyField(Outfit, blank=True, related_name="boards")
    products = models.ManyToManyField("products.Product", blank=True, related_name="style_boards")
    is_public = models.BooleanField(default=False)
    followers_count = models.PositiveIntegerField(default=0)
    followed_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL, blank=True, related_name="followed_boards"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.name} by {self.user.email}"
