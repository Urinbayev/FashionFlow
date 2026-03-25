"""
Product models: Product, Category, Collection, Size, Color, ProductVariant, ProductImage.
"""

import uuid

from django.db import models
from django.utils.text import slugify
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    """Hierarchical product categories using MPTT."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True)
    parent = TreeForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class MPTTMeta:
        order_insertion_by = ["sort_order", "name"]

    class Meta:
        verbose_name = "category"
        verbose_name_plural = "categories"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Color(models.Model):
    """Available colors for products."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, help_text="Hex color code, e.g. #FF5733")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Size(models.Model):
    """Available sizes for products."""

    SIZE_TYPE_CHOICES = [
        ("clothing", "Clothing"),
        ("shoes", "Shoes"),
        ("accessories", "Accessories"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=20)
    size_type = models.CharField(max_length=20, choices=SIZE_TYPE_CHOICES, default="clothing")
    sort_order = models.PositiveIntegerField(default=0)
    chest_min_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    chest_max_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    waist_min_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    waist_max_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    hip_min_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    hip_max_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    length_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    eu_equivalent = models.CharField(max_length=10, blank=True)
    uk_equivalent = models.CharField(max_length=10, blank=True)
    us_equivalent = models.CharField(max_length=10, blank=True)

    class Meta:
        ordering = ["size_type", "sort_order"]
        unique_together = ["name", "size_type"]

    def __str__(self):
        return f"{self.name} ({self.get_size_type_display()})"


class Collection(models.Model):
    """Seasonal or thematic product collections."""

    SEASON_CHOICES = [
        ("spring", "Spring"),
        ("summer", "Summer"),
        ("fall", "Fall"),
        ("winter", "Winter"),
        ("resort", "Resort"),
        ("pre_fall", "Pre-Fall"),
        ("all_season", "All Season"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True)
    description = models.TextField(blank=True)
    season = models.CharField(max_length=20, choices=SEASON_CHOICES, default="all_season")
    year = models.PositiveIntegerField(null=True, blank=True)
    cover_image = models.ImageField(upload_to="collections/covers/", blank=True)
    banner_image = models.ImageField(upload_to="collections/banners/", blank=True)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-publish_date"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Core product model."""

    GENDER_CHOICES = [
        ("M", "Men"),
        ("F", "Women"),
        ("U", "Unisex"),
        ("K", "Kids"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=300, db_index=True)
    slug = models.SlugField(max_length=320, unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=500, blank=True)
    brand = models.CharField(max_length=200, db_index=True)
    category = TreeForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    collections = models.ManyToManyField(Collection, blank=True, related_name="products")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, default="U")
    base_price = models.DecimalField(max_digits=10, decimal_places=2)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    material = models.CharField(max_length=300, blank=True)
    care_instructions = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_new_arrival = models.BooleanField(default=False)
    is_sustainable = models.BooleanField(default=False)
    sustainability_info = models.TextField(blank=True)
    available_colors = models.ManyToManyField(Color, blank=True, related_name="products")
    available_sizes = models.ManyToManyField(Size, blank=True, related_name="products")
    tags = models.JSONField(default=list, blank=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    review_count = models.PositiveIntegerField(default=0)
    total_sold = models.PositiveIntegerField(default=0)
    ranking_score = models.FloatField(default=0, db_index=True)
    virtual_tryon_enabled = models.BooleanField(default=False)
    virtual_tryon_asset = models.FileField(upload_to="products/tryon/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-ranking_score", "-created_at"]
        indexes = [
            models.Index(fields=["brand", "is_active"]),
            models.Index(fields=["category", "is_active"]),
            models.Index(fields=["-created_at", "is_active"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.brand}-{self.name}")
        super().save(*args, **kwargs)

    @property
    def current_price(self):
        return self.sale_price if self.sale_price else self.base_price

    @property
    def discount_percentage(self):
        if self.sale_price and self.base_price > 0:
            return round((1 - self.sale_price / self.base_price) * 100)
        return 0

    @property
    def in_stock(self):
        return self.variants.filter(stock__gt=0).exists()


class ProductVariant(models.Model):
    """Specific SKU combining product + size + color."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.ForeignKey(Size, on_delete=models.PROTECT, related_name="variants")
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="variants")
    sku = models.CharField(max_length=100, unique=True, db_index=True)
    stock = models.PositiveIntegerField(default=0)
    reserved_stock = models.PositiveIntegerField(default=0)
    price_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["product", "size", "color"]
        ordering = ["product", "color", "size"]

    def __str__(self):
        return f"{self.product.name} - {self.color.name} / {self.size.name} ({self.sku})"

    @property
    def available_stock(self):
        return max(0, self.stock - self.reserved_stock)

    @property
    def effective_price(self):
        return self.product.current_price + self.price_adjustment


class ProductImage(models.Model):
    """Product images, optionally linked to a specific color."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True, related_name="product_images")
    image = models.ImageField(upload_to="products/images/%Y/%m/")
    alt_text = models.CharField(max_length=300, blank=True)
    is_primary = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sort_order", "-is_primary"]

    def __str__(self):
        return f"Image for {self.product.name} (#{self.sort_order})"

    def save(self, *args, **kwargs):
        if self.is_primary:
            ProductImage.objects.filter(
                product=self.product, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)
