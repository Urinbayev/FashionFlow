"""
Review URL configuration.
"""

from django.urls import path
from . import views

app_name = "reviews"

urlpatterns = [
    path("", views.ReviewListView.as_view(), name="review-list"),
    path("create/", views.ReviewCreateView.as_view(), name="review-create"),
    path("<uuid:pk>/helpful/", views.ReviewHelpfulView.as_view(), name="review-helpful"),
    path("stats/<uuid:product_id>/", views.ReviewStatsView.as_view(), name="review-stats"),
]
