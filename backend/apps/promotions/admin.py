"""
Promotion admin configuration.
"""

from django.contrib import admin
from .models import Promotion, Coupon, CouponUsage, FlashSale


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ["name", "promo_type", "discount_value", "start_date", "end_date", "is_active"]
    list_filter = ["promo_type", "is_active"]
    search_fields = ["name", "description"]
    filter_horizontal = ["applicable_categories", "applicable_products", "applicable_collections"]


class CouponUsageInline(admin.TabularInline):
    model = CouponUsage
    extra = 0
    readonly_fields = ["user", "order", "discount_applied", "used_at"]


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        "code", "discount_type", "discount_value", "current_uses",
        "max_uses", "start_date", "end_date", "is_active", "influencer",
    ]
    list_filter = ["discount_type", "is_active"]
    search_fields = ["code", "description"]
    raw_id_fields = ["influencer"]
    filter_horizontal = ["applicable_categories", "applicable_products"]
    inlines = [CouponUsageInline]


@admin.register(FlashSale)
class FlashSaleAdmin(admin.ModelAdmin):
    list_display = ["name", "discount_percentage", "start_time", "end_time", "is_active", "is_live"]
    list_filter = ["is_active"]
    search_fields = ["name"]
    filter_horizontal = ["products"]
