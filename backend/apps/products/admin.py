"""
Product admin configuration.
"""

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from .models import Category, Color, Size, Collection, Product, ProductVariant, ProductImage


@admin.register(Category)
class CategoryAdmin(DraggableMPTTAdmin):
    list_display = ["tree_actions", "indented_title", "slug", "is_active", "sort_order"]
    list_display_links = ["indented_title"]
    list_filter = ["is_active"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ["name", "hex_code", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ["name", "size_type", "sort_order", "eu_equivalent", "us_equivalent"]
    list_filter = ["size_type"]
    ordering = ["size_type", "sort_order"]


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ["image", "color", "alt_text", "is_primary", "sort_order"]


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ["sku", "size", "color", "stock", "reserved_stock", "price_adjustment", "is_active"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "name", "brand", "category", "base_price", "sale_price",
        "is_active", "is_featured", "is_new_arrival", "average_rating", "total_sold",
    ]
    list_filter = [
        "is_active", "is_featured", "is_new_arrival", "is_sustainable",
        "gender", "category", "brand", "virtual_tryon_enabled",
    ]
    search_fields = ["name", "brand", "description"]
    prepopulated_fields = {"slug": ("brand", "name")}
    filter_horizontal = ["collections", "available_colors", "available_sizes"]
    inlines = [ProductImageInline, ProductVariantInline]
    readonly_fields = ["average_rating", "review_count", "total_sold", "ranking_score"]

    fieldsets = (
        (None, {"fields": ("name", "slug", "brand", "category", "gender")}),
        ("Description", {"fields": ("description", "short_description")}),
        ("Pricing", {"fields": ("base_price", "sale_price")}),
        ("Details", {"fields": ("material", "care_instructions", "tags")}),
        ("Flags", {"fields": ("is_active", "is_featured", "is_new_arrival", "is_sustainable", "sustainability_info")}),
        ("Virtual Try-On", {"fields": ("virtual_tryon_enabled", "virtual_tryon_asset")}),
        ("Collections & Options", {"fields": ("collections", "available_colors", "available_sizes")}),
        ("Stats (read only)", {"fields": ("average_rating", "review_count", "total_sold", "ranking_score")}),
    )


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "season", "year", "is_featured", "is_active", "publish_date"]
    list_filter = ["season", "year", "is_featured", "is_active"]
    search_fields = ["name", "description"]
    prepopulated_fields = {"slug": ("name",)}


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ["sku", "product", "size", "color", "stock", "available_stock", "is_active"]
    list_filter = ["is_active", "color", "size"]
    search_fields = ["sku", "product__name"]
    raw_id_fields = ["product"]
