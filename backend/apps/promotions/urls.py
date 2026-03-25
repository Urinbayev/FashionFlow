"""
Promotion URL configuration.
"""

from django.urls import path
from . import views

app_name = "promotions"

urlpatterns = [
    path("", views.ActivePromotionsView.as_view(), name="active-promotions"),
    path("validate/", views.CouponValidateView.as_view(), name="coupon-validate"),
    path("flash-sales/", views.FlashSaleListView.as_view(), name="flash-sale-list"),
    path("flash-sales/<uuid:pk>/", views.FlashSaleDetailView.as_view(), name="flash-sale-detail"),
]
