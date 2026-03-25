"""
Outfit URL configuration.
"""

from django.urls import path
from . import views

app_name = "outfits"

urlpatterns = [
    path("", views.OutfitListCreateView.as_view(), name="outfit-list"),
    path("my/", views.MyOutfitsView.as_view(), name="my-outfits"),
    path("<uuid:pk>/", views.OutfitDetailView.as_view(), name="outfit-detail"),
    path("<uuid:pk>/like/", views.OutfitLikeView.as_view(), name="outfit-like"),
    path("boards/", views.StyleBoardListCreateView.as_view(), name="board-list"),
    path("boards/<uuid:pk>/", views.StyleBoardDetailView.as_view(), name="board-detail"),
    path("boards/<uuid:pk>/add/", views.StyleBoardAddItemView.as_view(), name="board-add-item"),
]
