"""
Product URL configuration.
"""

from django.urls import path
from . import views

app_name = "products"

urlpatterns = [
    path("", views.ProductListView.as_view(), name="product-list"),
    path("featured/", views.FeaturedProductsView.as_view(), name="featured"),
    path("new-arrivals/", views.NewArrivalsView.as_view(), name="new-arrivals"),
    path("categories/", views.CategoryListView.as_view(), name="category-list"),
    path("categories/<slug:slug>/", views.CategoryDetailView.as_view(), name="category-detail"),
    path("collections/", views.CollectionListView.as_view(), name="collection-list"),
    path("collections/<slug:slug>/", views.CollectionDetailView.as_view(), name="collection-detail"),
    path("colors/", views.ColorListView.as_view(), name="color-list"),
    path("sizes/", views.SizeListView.as_view(), name="size-list"),
    path("<slug:slug>/", views.ProductDetailView.as_view(), name="product-detail"),
]
