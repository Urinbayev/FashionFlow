"""
Review models: Review, ReviewImage, ReviewHelpful.
"""

import uuid

from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Review(models.Model):
    """Product review with rating, fit feedback, and optional photos."""

    FIT_CHOICES = [
        ("runs_small", "Runs Small"),
        ("true_to_size", "True to Size"),
        ("runs_large", "Runs Large"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews")
    order_item = models.ForeignKey(
        "orders.OrderItem", on_delete=models.SET_NULL, null=True, blank=True, related_name="review"
    )
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    title = models.CharField(max_length=200)
    body = models.TextField()
    fit = models.CharField(max_length=20, choices=FIT_CHOICES, blank=True)
    size_purchased = models.CharField(max_length=20, blank=True)
    color_purchased = models.CharField(max_length=50, blank=True)
    would_recommend = models.BooleanField(default=True)
    helpful_count = models.PositiveIntegerField(default=0)
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["product", "user"]

    def __str__(self):
        return f"Review by {self.user.email} for {self.product.name} ({self.rating}/5)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._update_product_rating()

    def delete(self, *args, **kwargs):
        product = self.product
        super().delete(*args, **kwargs)
        self._update_product_rating(product=product)

    def _update_product_rating(self, product=None):
        product = product or self.product
        stats = product.reviews.filter(is_approved=True).aggregate(
            avg_rating=Avg("rating"),
            count=models.Count("id"),
        )
        product.average_rating = stats["avg_rating"] or 0
        product.review_count = stats["count"]
        product.save(update_fields=["average_rating", "review_count"])


class ReviewImage(models.Model):
    """Photo attached to a review."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="reviews/%Y/%m/")
    caption = models.CharField(max_length=300, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Image for review {self.review.id}"


class ReviewHelpful(models.Model):
    """Tracks which users marked a review as helpful."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name="helpful_votes")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="helpful_votes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["review", "user"]

    def __str__(self):
        return f"{self.user.email} found review {self.review.id} helpful"
