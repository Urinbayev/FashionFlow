"""
Product filters for the catalog API.
"""

import django_filters

from .models import Product


class ProductFilter(django_filters.FilterSet):
    """
    Rich filtering for product listings.
    Supports filtering by price range, category, brand, color, size,
    gender, collection, and various boolean flags.
    """

    min_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="base_price", lookup_expr="lte")
    category = django_filters.UUIDFilter(field_name="category__id")
    category_slug = django_filters.CharFilter(field_name="category__slug")
    brand = django_filters.CharFilter(field_name="brand", lookup_expr="iexact")
    brands = django_filters.CharFilter(method="filter_brands")
    color = django_filters.UUIDFilter(field_name="available_colors__id")
    colors = django_filters.CharFilter(method="filter_colors")
    size = django_filters.UUIDFilter(field_name="available_sizes__id")
    sizes = django_filters.CharFilter(method="filter_sizes")
    gender = django_filters.CharFilter(field_name="gender")
    collection = django_filters.UUIDFilter(field_name="collections__id")
    collection_slug = django_filters.CharFilter(field_name="collections__slug")
    is_featured = django_filters.BooleanFilter()
    is_new_arrival = django_filters.BooleanFilter()
    is_sustainable = django_filters.BooleanFilter()
    on_sale = django_filters.BooleanFilter(method="filter_on_sale")
    in_stock = django_filters.BooleanFilter(method="filter_in_stock")
    virtual_tryon = django_filters.BooleanFilter(field_name="virtual_tryon_enabled")

    class Meta:
        model = Product
        fields = []

    def filter_brands(self, queryset, name, value):
        brands = [b.strip() for b in value.split(",")]
        return queryset.filter(brand__in=brands)

    def filter_colors(self, queryset, name, value):
        color_ids = [c.strip() for c in value.split(",")]
        return queryset.filter(available_colors__id__in=color_ids).distinct()

    def filter_sizes(self, queryset, name, value):
        size_ids = [s.strip() for s in value.split(",")]
        return queryset.filter(available_sizes__id__in=size_ids).distinct()

    def filter_on_sale(self, queryset, name, value):
        if value:
            return queryset.filter(sale_price__isnull=False, sale_price__lt=models.F("base_price"))
        return queryset.filter(sale_price__isnull=True)

    def filter_in_stock(self, queryset, name, value):
        if value:
            return queryset.filter(variants__stock__gt=0).distinct()
        return queryset.filter(variants__stock=0).distinct()


# Import models.F for the on_sale filter
from django.db import models  # noqa: E402
