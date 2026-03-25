"""
Product views for catalog browsing, categories, and collections.
"""

from django.db.models import Prefetch
from rest_framework import generics, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category, Collection, Color, Size, ProductImage
from .serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    CategorySerializer,
    CollectionListSerializer,
    CollectionDetailSerializer,
    ColorSerializer,
    SizeSerializer,
)
from .filters import ProductFilter


class ProductListView(generics.ListAPIView):
    """
    List products with rich filtering, searching, and ordering.

    Supports filtering by category, brand, color, size, gender,
    price range, collection, sale status, and stock availability.
    """

    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "brand", "description", "tags"]
    ordering_fields = ["base_price", "created_at", "average_rating", "total_sold", "ranking_score", "name"]
    ordering = ["-ranking_score"]

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category").prefetch_related(
            Prefetch("images", queryset=ProductImage.objects.filter(is_primary=True)[:1])
        )


class ProductDetailView(generics.RetrieveAPIView):
    """Retrieve full product detail by slug."""

    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Product.objects.filter(is_active=True).select_related("category").prefetch_related(
            "images", "variants__size", "variants__color",
            "available_colors", "available_sizes", "collections",
        )


class CategoryListView(generics.ListAPIView):
    """List root-level categories with nested children."""

    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Category.objects.filter(is_active=True, parent=None).prefetch_related("children")


class CategoryDetailView(generics.RetrieveAPIView):
    """Retrieve category detail with children."""

    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Category.objects.filter(is_active=True)


class CollectionListView(generics.ListAPIView):
    """List active collections."""

    serializer_class = CollectionListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["season", "year", "is_featured"]
    ordering_fields = ["publish_date", "name"]
    ordering = ["-is_featured", "-publish_date"]

    def get_queryset(self):
        return Collection.objects.filter(is_active=True)


class CollectionDetailView(generics.RetrieveAPIView):
    """Retrieve collection detail with products."""

    serializer_class = CollectionDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Collection.objects.filter(is_active=True).prefetch_related(
            "products__images", "products__category",
        )


class ColorListView(generics.ListAPIView):
    """List all available colors."""

    serializer_class = ColorSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Color.objects.filter(is_active=True)


class SizeListView(generics.ListAPIView):
    """List all available sizes, optionally filtered by type."""

    serializer_class = SizeSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filterset_fields = ["size_type"]

    def get_queryset(self):
        return Size.objects.all()


class FeaturedProductsView(generics.ListAPIView):
    """List featured products for homepage."""

    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True, is_featured=True
        ).select_related("category")[:12]


class NewArrivalsView(generics.ListAPIView):
    """List new arrival products."""

    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Product.objects.filter(
            is_active=True, is_new_arrival=True
        ).select_related("category").order_by("-created_at")
