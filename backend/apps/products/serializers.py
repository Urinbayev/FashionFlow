"""
Product serializers for catalog, categories, collections, and variants.
"""

from rest_framework import serializers
from .models import Category, Color, Size, Collection, Product, ProductVariant, ProductImage


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ["id", "name", "hex_code"]


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = [
            "id", "name", "size_type", "sort_order",
            "chest_min_cm", "chest_max_cm",
            "waist_min_cm", "waist_max_cm",
            "hip_min_cm", "hip_max_cm",
            "length_cm", "eu_equivalent", "uk_equivalent", "us_equivalent",
        ]


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "description", "image", "parent", "children", "product_count"]

    def get_children(self, obj):
        children = obj.get_children().filter(is_active=True)
        return CategorySerializer(children, many=True).data

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CategoryListSerializer(serializers.ModelSerializer):
    """Flat category serializer for filter dropdowns."""

    full_path = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ["id", "name", "slug", "full_path"]

    def get_full_path(self, obj):
        ancestors = obj.get_ancestors(include_self=True)
        return " > ".join([a.name for a in ancestors])


class ProductImageSerializer(serializers.ModelSerializer):
    color_name = serializers.CharField(source="color.name", read_only=True, default=None)

    class Meta:
        model = ProductImage
        fields = ["id", "image", "alt_text", "is_primary", "sort_order", "color", "color_name"]


class ProductVariantSerializer(serializers.ModelSerializer):
    size_detail = SizeSerializer(source="size", read_only=True)
    color_detail = ColorSerializer(source="color", read_only=True)
    available_stock = serializers.ReadOnlyField()
    effective_price = serializers.ReadOnlyField()

    class Meta:
        model = ProductVariant
        fields = [
            "id", "sku", "size", "color", "size_detail", "color_detail",
            "stock", "available_stock", "price_adjustment", "effective_price", "is_active",
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for product listings."""

    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    category_name = serializers.CharField(source="category.name", read_only=True)
    primary_image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "brand", "category", "category_name",
            "gender", "base_price", "sale_price", "current_price",
            "discount_percentage", "in_stock", "is_new_arrival",
            "is_sustainable", "average_rating", "review_count",
            "primary_image", "virtual_tryon_enabled",
        ]

    def get_primary_image(self, obj):
        image = obj.images.filter(is_primary=True).first()
        if not image:
            image = obj.images.first()
        if image:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(image.image.url)
            return image.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """Full product detail serializer."""

    current_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    in_stock = serializers.ReadOnlyField()
    category_detail = CategoryListSerializer(source="category", read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    available_colors = ColorSerializer(many=True, read_only=True)
    available_sizes = SizeSerializer(many=True, read_only=True)
    related_products = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "name", "slug", "description", "short_description",
            "brand", "category", "category_detail", "gender",
            "base_price", "sale_price", "current_price", "discount_percentage",
            "material", "care_instructions", "in_stock",
            "is_featured", "is_new_arrival", "is_sustainable", "sustainability_info",
            "images", "variants", "available_colors", "available_sizes",
            "tags", "average_rating", "review_count", "total_sold",
            "virtual_tryon_enabled", "related_products",
            "created_at", "updated_at",
        ]

    def get_related_products(self, obj):
        related = Product.objects.filter(
            category=obj.category, is_active=True
        ).exclude(id=obj.id).order_by("-ranking_score")[:8]
        return ProductListSerializer(related, many=True, context=self.context).data


class CollectionListSerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()

    class Meta:
        model = Collection
        fields = [
            "id", "name", "slug", "description", "season", "year",
            "cover_image", "is_featured", "product_count", "publish_date",
        ]

    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CollectionDetailSerializer(serializers.ModelSerializer):
    products = ProductListSerializer(many=True, read_only=True)

    class Meta:
        model = Collection
        fields = [
            "id", "name", "slug", "description", "season", "year",
            "cover_image", "banner_image", "is_featured",
            "products", "publish_date", "created_at",
        ]
