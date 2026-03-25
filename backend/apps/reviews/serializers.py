"""
Review serializers.
"""

from rest_framework import serializers

from .models import Review, ReviewImage, ReviewHelpful


class ReviewImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewImage
        fields = ["id", "image", "caption"]


class ReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    images = ReviewImageSerializer(many=True, read_only=True)
    is_helpful_by_me = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id", "product", "user_name", "rating", "title", "body",
            "fit", "size_purchased", "color_purchased", "would_recommend",
            "helpful_count", "is_verified_purchase", "is_helpful_by_me",
            "images", "created_at",
        ]
        read_only_fields = ["id", "helpful_count", "is_verified_purchase", "created_at"]

    def get_is_helpful_by_me(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.helpful_votes.filter(user=request.user).exists()
        return False


class ReviewCreateSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(), required=False, max_length=5
    )

    class Meta:
        model = Review
        fields = [
            "product", "rating", "title", "body",
            "fit", "size_purchased", "color_purchased",
            "would_recommend", "images",
        ]

    def validate(self, attrs):
        user = self.context["request"].user
        product = attrs["product"]
        if Review.objects.filter(product=product, user=user).exists():
            raise serializers.ValidationError("You have already reviewed this product.")
        return attrs

    def create(self, validated_data):
        images_data = validated_data.pop("images", [])
        user = self.context["request"].user
        validated_data["user"] = user

        # Check if user has a delivered order with this product
        from apps.orders.models import OrderItem
        has_purchase = OrderItem.objects.filter(
            order__user=user,
            order__status="delivered",
            variant__product=validated_data["product"],
        ).exists()
        validated_data["is_verified_purchase"] = has_purchase

        review = Review.objects.create(**validated_data)

        for image in images_data:
            ReviewImage.objects.create(review=review, image=image)

        return review


class ReviewStatsSerializer(serializers.Serializer):
    """Aggregated review statistics for a product."""

    average_rating = serializers.FloatField()
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()
    fit_distribution = serializers.DictField()
    recommendation_percentage = serializers.FloatField()
