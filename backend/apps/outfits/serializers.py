"""
Outfit serializers for outfit builder and style boards.
"""

from rest_framework import serializers

from apps.products.serializers import ProductListSerializer
from .models import Outfit, OutfitItem, StyleBoard


class OutfitItemSerializer(serializers.ModelSerializer):
    product_detail = ProductListSerializer(source="product", read_only=True)

    class Meta:
        model = OutfitItem
        fields = ["id", "product", "product_detail", "slot", "notes", "sort_order"]


class OutfitItemCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutfitItem
        fields = ["product", "slot", "notes", "sort_order"]


class OutfitListSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    item_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Outfit
        fields = [
            "id", "name", "description", "occasion", "season",
            "cover_image", "is_public", "likes_count", "is_liked",
            "total_price", "user_name", "item_count", "created_at",
        ]

    def get_item_count(self, obj):
        return obj.items.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False


class OutfitDetailSerializer(serializers.ModelSerializer):
    items = OutfitItemSerializer(many=True, read_only=True)
    user_name = serializers.CharField(source="user.full_name", read_only=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Outfit
        fields = [
            "id", "name", "description", "occasion", "season",
            "cover_image", "is_public", "is_featured", "likes_count",
            "is_liked", "tags", "total_price", "user_name",
            "items", "created_at", "updated_at",
        ]

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return obj.liked_by.filter(id=request.user.id).exists()
        return False


class OutfitCreateSerializer(serializers.ModelSerializer):
    items = OutfitItemCreateSerializer(many=True)

    class Meta:
        model = Outfit
        fields = [
            "name", "description", "occasion", "season",
            "cover_image", "is_public", "tags", "items",
        ]

    def create(self, validated_data):
        items_data = validated_data.pop("items")
        outfit = Outfit.objects.create(
            user=self.context["request"].user, **validated_data
        )
        for item_data in items_data:
            OutfitItem.objects.create(outfit=outfit, **item_data)
        outfit.calculate_total_price()
        return outfit

    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                OutfitItem.objects.create(outfit=instance, **item_data)
            instance.calculate_total_price()

        return instance


class StyleBoardListSerializer(serializers.ModelSerializer):
    outfit_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = StyleBoard
        fields = [
            "id", "name", "description", "cover_image",
            "is_public", "followers_count", "outfit_count",
            "product_count", "created_at", "updated_at",
        ]

    def get_outfit_count(self, obj):
        return obj.outfits.count()

    def get_product_count(self, obj):
        return obj.products.count()


class StyleBoardDetailSerializer(serializers.ModelSerializer):
    outfits = OutfitListSerializer(many=True, read_only=True)
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = StyleBoard
        fields = [
            "id", "name", "description", "cover_image",
            "is_public", "followers_count", "outfits",
            "products", "created_at", "updated_at",
        ]


class StyleBoardCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StyleBoard
        fields = ["name", "description", "cover_image", "is_public"]

    def create(self, validated_data):
        return StyleBoard.objects.create(
            user=self.context["request"].user, **validated_data
        )
