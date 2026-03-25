"""
Order serializers for order management, returns, and refunds.
"""

from rest_framework import serializers

from apps.products.models import ProductVariant
from .models import Order, OrderItem, Return, Refund


class OrderItemCreateSerializer(serializers.Serializer):
    """Serializer for creating order items from cart data."""

    variant_id = serializers.UUIDField()
    quantity = serializers.IntegerField(min_value=1, max_value=50)

    def validate_variant_id(self, value):
        try:
            variant = ProductVariant.objects.select_related(
                "product", "size", "color"
            ).get(id=value, is_active=True)
        except ProductVariant.DoesNotExist:
            raise serializers.ValidationError("Product variant not found or unavailable.")
        if variant.available_stock < 1:
            raise serializers.ValidationError(f"'{variant.product.name}' in {variant.size.name}/{variant.color.name} is out of stock.")
        return value

    def validate(self, attrs):
        variant = ProductVariant.objects.get(id=attrs["variant_id"])
        if variant.available_stock < attrs["quantity"]:
            raise serializers.ValidationError(
                f"Only {variant.available_stock} units available for '{variant.product.name}'."
            )
        return attrs


class OrderItemReadSerializer(serializers.ModelSerializer):
    """Serializer for reading order items."""

    class Meta:
        model = OrderItem
        fields = [
            "id", "product_name", "product_brand", "size_name",
            "color_name", "sku", "quantity", "unit_price", "line_total",
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating a new order."""

    items = OrderItemCreateSerializer(many=True, min_length=1)
    shipping_name = serializers.CharField(max_length=200)
    shipping_phone = serializers.CharField(max_length=20, required=False, default="")
    shipping_address_1 = serializers.CharField(max_length=255)
    shipping_address_2 = serializers.CharField(max_length=255, required=False, default="")
    shipping_city = serializers.CharField(max_length=100)
    shipping_state = serializers.CharField(max_length=100, required=False, default="")
    shipping_postal_code = serializers.CharField(max_length=20)
    shipping_country = serializers.CharField(max_length=100, default="US")
    shipping_method = serializers.CharField(max_length=100, required=False, default="standard")
    coupon_code = serializers.CharField(max_length=50, required=False, default="")
    notes = serializers.CharField(required=False, default="")
    payment_method = serializers.CharField(max_length=50, default="stripe")

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        user = self.context["request"].user

        order = Order.objects.create(user=user, **validated_data)

        for item_data in items_data:
            variant = ProductVariant.objects.select_related(
                "product", "size", "color"
            ).get(id=item_data["variant_id"])

            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                product_brand=variant.product.brand,
                size_name=variant.size.name,
                color_name=variant.color.name,
                sku=variant.sku,
                quantity=item_data["quantity"],
                unit_price=variant.effective_price,
            )

            # Reserve stock
            variant.reserved_stock += item_data["quantity"]
            variant.save(update_fields=["reserved_stock"])

        order.calculate_totals()
        return order


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list views."""

    item_count = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "payment_status",
            "total", "item_count", "created_at", "estimated_delivery",
        ]

    def get_item_count(self, obj):
        return obj.items.count()


class OrderDetailSerializer(serializers.ModelSerializer):
    """Full order detail serializer."""

    items = OrderItemReadSerializer(many=True, read_only=True)
    returns = serializers.SerializerMethodField()
    refunds = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "order_number", "status", "payment_status", "payment_method",
            "shipping_name", "shipping_phone", "shipping_address_1", "shipping_address_2",
            "shipping_city", "shipping_state", "shipping_postal_code", "shipping_country",
            "subtotal", "shipping_cost", "tax_amount", "discount_amount", "total",
            "coupon_code", "shipping_method", "tracking_number", "tracking_url",
            "estimated_delivery", "notes",
            "items", "returns", "refunds",
            "shipped_at", "delivered_at", "cancelled_at", "created_at", "updated_at",
        ]

    def get_returns(self, obj):
        return ReturnSerializer(obj.returns.all(), many=True).data

    def get_refunds(self, obj):
        return RefundSerializer(obj.refunds.all(), many=True).data


class ReturnCreateSerializer(serializers.Serializer):
    """Serializer for creating a return request."""

    item_ids = serializers.ListField(child=serializers.UUIDField(), min_length=1)
    reason = serializers.ChoiceField(choices=Return.REASON_CHOICES)
    reason_detail = serializers.CharField(required=False, default="")

    def validate_item_ids(self, value):
        order = self.context["order"]
        valid_item_ids = set(order.items.values_list("id", flat=True))
        for item_id in value:
            if item_id not in valid_item_ids:
                raise serializers.ValidationError(f"Item {item_id} does not belong to this order.")
        return value

    def create(self, validated_data):
        order = self.context["order"]
        item_ids = validated_data.pop("item_ids")
        return_request = Return.objects.create(order=order, **validated_data)
        return_request.items.set(OrderItem.objects.filter(id__in=item_ids))
        return return_request


class ReturnSerializer(serializers.ModelSerializer):
    class Meta:
        model = Return
        fields = [
            "id", "reason", "reason_detail", "status",
            "return_tracking_number", "created_at", "updated_at",
        ]


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = [
            "id", "amount", "method", "reason",
            "processed_at", "created_at",
        ]
