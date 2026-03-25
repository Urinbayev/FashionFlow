"""
Order admin configuration.
"""

from django.contrib import admin

from .models import Order, OrderItem, Return, Refund


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "product_brand", "size_name", "color_name", "sku", "unit_price", "line_total"]
    fields = ["product_name", "size_name", "color_name", "sku", "quantity", "unit_price", "line_total"]


class ReturnInline(admin.TabularInline):
    model = Return
    extra = 0
    fields = ["reason", "status", "return_tracking_number", "created_at"]
    readonly_fields = ["created_at"]


class RefundInline(admin.TabularInline):
    model = Refund
    extra = 0
    fields = ["amount", "method", "reason", "processed_at"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "order_number", "user", "status", "payment_status",
        "total", "shipping_city", "shipping_country", "created_at",
    ]
    list_filter = ["status", "payment_status", "shipping_country", "created_at"]
    search_fields = ["order_number", "user__email", "shipping_name", "tracking_number"]
    readonly_fields = [
        "order_number", "subtotal", "total", "created_at", "updated_at",
        "shipped_at", "delivered_at", "cancelled_at",
    ]
    raw_id_fields = ["user"]
    inlines = [OrderItemInline, ReturnInline, RefundInline]

    fieldsets = (
        (None, {"fields": ("order_number", "user", "status", "payment_status", "payment_method")}),
        ("Shipping Address", {"fields": (
            "shipping_name", "shipping_phone", "shipping_address_1", "shipping_address_2",
            "shipping_city", "shipping_state", "shipping_postal_code", "shipping_country",
        )}),
        ("Totals", {"fields": (
            "subtotal", "shipping_cost", "tax_amount", "discount_amount", "total",
        )}),
        ("Shipping & Tracking", {"fields": (
            "shipping_method", "tracking_number", "tracking_url", "estimated_delivery",
        )}),
        ("Promo", {"fields": ("coupon_code", "influencer_code")}),
        ("Notes", {"fields": ("notes",)}),
        ("Timestamps", {"fields": (
            "created_at", "updated_at", "shipped_at", "delivered_at", "cancelled_at",
        )}),
    )


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ["order", "reason", "status", "created_at"]
    list_filter = ["status", "reason"]
    search_fields = ["order__order_number"]
    raw_id_fields = ["order"]
    filter_horizontal = ["items"]


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ["order", "amount", "method", "processed_at", "created_at"]
    list_filter = ["method"]
    search_fields = ["order__order_number"]
    raw_id_fields = ["order", "return_request"]
