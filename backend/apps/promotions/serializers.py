"""
Promotion serializers for coupons, flash sales, and promotions.
"""

from rest_framework import serializers

from apps.products.serializers import ProductListSerializer
from .models import Promotion, Coupon, CouponUsage, FlashSale


class PromotionSerializer(serializers.ModelSerializer):
    is_currently_active = serializers.ReadOnlyField()

    class Meta:
        model = Promotion
        fields = [
            "id", "name", "description", "promo_type", "discount_value",
            "min_purchase_amount", "max_discount_amount", "banner_image",
            "start_date", "end_date", "is_currently_active",
        ]


class CouponValidateSerializer(serializers.Serializer):
    """Serializer for validating a coupon code."""

    code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, required=False, default=0)


class CouponResponseSerializer(serializers.Serializer):
    """Response after validating a coupon."""

    valid = serializers.BooleanField()
    code = serializers.CharField()
    discount_type = serializers.CharField()
    discount_value = serializers.DecimalField(max_digits=10, decimal_places=2)
    calculated_discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    min_purchase_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    message = serializers.CharField()


class FlashSaleListSerializer(serializers.ModelSerializer):
    is_live = serializers.ReadOnlyField()
    time_remaining_seconds = serializers.ReadOnlyField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = FlashSale
        fields = [
            "id", "name", "description", "discount_percentage",
            "start_time", "end_time", "banner_image",
            "is_live", "time_remaining_seconds", "product_count",
            "max_quantity_per_user",
        ]

    def get_product_count(self, obj):
        return obj.products.count()


class FlashSaleDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)
    is_live = serializers.ReadOnlyField()
    time_remaining_seconds = serializers.ReadOnlyField()

    class Meta:
        model = FlashSale
        fields = [
            "id", "name", "description", "discount_percentage",
            "start_time", "end_time", "banner_image",
            "is_live", "time_remaining_seconds",
            "max_quantity_per_user", "products",
        ]
