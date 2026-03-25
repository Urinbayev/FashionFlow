"""
Order models: Order, OrderItem, Return, Refund.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Order(models.Model):
    """Customer order containing one or more items."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
        ("partially_refunded", "Partially Refunded"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order_number = models.CharField(max_length=30, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="orders")

    # Shipping address (snapshot at order time)
    shipping_name = models.CharField(max_length=200)
    shipping_phone = models.CharField(max_length=20, blank=True)
    shipping_address_1 = models.CharField(max_length=255)
    shipping_address_2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100, blank=True)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default="US")

    # Billing address
    billing_name = models.CharField(max_length=200, blank=True)
    billing_address_1 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100, blank=True)
    billing_postal_code = models.CharField(max_length=20, blank=True)
    billing_country = models.CharField(max_length=100, blank=True)

    # Totals
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending", db_index=True)
    payment_status = models.CharField(max_length=25, choices=PAYMENT_STATUS_CHOICES, default="pending")
    payment_method = models.CharField(max_length=50, blank=True)
    stripe_payment_intent_id = models.CharField(max_length=255, blank=True)

    # Coupon / Promo
    coupon_code = models.CharField(max_length=50, blank=True)
    influencer_code = models.CharField(max_length=50, blank=True)

    # Shipping
    shipping_method = models.CharField(max_length=100, blank=True)
    tracking_number = models.CharField(max_length=200, blank=True)
    tracking_url = models.URLField(blank=True)
    estimated_delivery = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)
    shipped_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["-created_at"]),
        ]

    def __str__(self):
        return f"Order {self.order_number}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_order_number():
        now = timezone.now()
        prefix = now.strftime("FF%Y%m%d")
        last_order = Order.objects.filter(
            order_number__startswith=prefix
        ).order_by("-order_number").first()
        if last_order:
            last_seq = int(last_order.order_number[-5:])
            seq = last_seq + 1
        else:
            seq = 1
        return f"{prefix}{seq:05d}"

    def calculate_totals(self):
        self.subtotal = sum(item.line_total for item in self.items.all())
        self.total = self.subtotal + self.shipping_cost + self.tax_amount - self.discount_amount
        self.save(update_fields=["subtotal", "total"])


class OrderItem(models.Model):
    """Individual line item within an order."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey(
        "products.ProductVariant", on_delete=models.PROTECT, related_name="order_items"
    )
    product_name = models.CharField(max_length=300)
    product_brand = models.CharField(max_length=200)
    size_name = models.CharField(max_length=50)
    color_name = models.CharField(max_length=50)
    sku = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    line_total = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def save(self, *args, **kwargs):
        self.line_total = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class Return(models.Model):
    """Return request for an order or specific items."""

    REASON_CHOICES = [
        ("wrong_size", "Wrong Size"),
        ("wrong_item", "Wrong Item Received"),
        ("defective", "Defective/Damaged"),
        ("not_as_described", "Not As Described"),
        ("changed_mind", "Changed My Mind"),
        ("other", "Other"),
    ]

    STATUS_CHOICES = [
        ("requested", "Requested"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("shipped_back", "Shipped Back"),
        ("received", "Received"),
        ("completed", "Completed"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="returns")
    items = models.ManyToManyField(OrderItem, related_name="returns")
    reason = models.CharField(max_length=30, choices=REASON_CHOICES)
    reason_detail = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="requested")
    return_tracking_number = models.CharField(max_length=200, blank=True)
    admin_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Return for {self.order.order_number} ({self.get_status_display()})"


class Refund(models.Model):
    """Refund record linked to a return or order cancellation."""

    REFUND_METHOD_CHOICES = [
        ("original_payment", "Original Payment Method"),
        ("store_credit", "Store Credit"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="refunds")
    return_request = models.ForeignKey(Return, on_delete=models.SET_NULL, null=True, blank=True, related_name="refunds")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=20, choices=REFUND_METHOD_CHOICES, default="original_payment")
    stripe_refund_id = models.CharField(max_length=255, blank=True)
    reason = models.TextField(blank=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Refund ${self.amount} for {self.order.order_number}"
