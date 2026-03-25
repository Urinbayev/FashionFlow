"""
Outfit views for outfit builder, discovery, and style boards.
"""

from django.db.models import Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Outfit, StyleBoard
from .serializers import (
    OutfitListSerializer,
    OutfitDetailSerializer,
    OutfitCreateSerializer,
    StyleBoardListSerializer,
    StyleBoardDetailSerializer,
    StyleBoardCreateSerializer,
)


class OutfitListCreateView(generics.ListCreateAPIView):
    """List public outfits or create a new outfit."""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return OutfitCreateSerializer
        return OutfitListSerializer

    def get_queryset(self):
        queryset = Outfit.objects.select_related("user").prefetch_related("items__product")
        if self.request.user.is_authenticated:
            queryset = queryset.filter(Q(is_public=True) | Q(user=self.request.user))
        else:
            queryset = queryset.filter(is_public=True)

        # Filtering
        occasion = self.request.query_params.get("occasion")
        season = self.request.query_params.get("season")
        if occasion:
            queryset = queryset.filter(occasion=occasion)
        if season:
            queryset = queryset.filter(season=season)

        return queryset


class OutfitDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete an outfit."""

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return OutfitCreateSerializer
        return OutfitDetailSerializer

    def get_queryset(self):
        queryset = Outfit.objects.select_related("user").prefetch_related(
            "items__product__images", "items__product__category"
        )
        if self.request.user.is_authenticated:
            return queryset.filter(Q(is_public=True) | Q(user=self.request.user))
        return queryset.filter(is_public=True)

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE"):
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

    def perform_update(self, serializer):
        outfit = self.get_object()
        if outfit.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only edit your own outfits.")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own outfits.")
        instance.delete()


class MyOutfitsView(generics.ListAPIView):
    """List outfits created by the current user."""

    serializer_class = OutfitListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Outfit.objects.filter(user=self.request.user).prefetch_related("items")


class OutfitLikeView(APIView):
    """Like or unlike an outfit."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            outfit = Outfit.objects.get(id=pk)
        except Outfit.DoesNotExist:
            return Response({"error": "Outfit not found."}, status=status.HTTP_404_NOT_FOUND)

        if outfit.liked_by.filter(id=request.user.id).exists():
            outfit.liked_by.remove(request.user)
            outfit.likes_count = max(0, outfit.likes_count - 1)
            outfit.save(update_fields=["likes_count"])
            return Response({"liked": False, "likes_count": outfit.likes_count})
        else:
            outfit.liked_by.add(request.user)
            outfit.likes_count += 1
            outfit.save(update_fields=["likes_count"])
            return Response({"liked": True, "likes_count": outfit.likes_count})


class StyleBoardListCreateView(generics.ListCreateAPIView):
    """List user's style boards or create a new one."""

    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return StyleBoardCreateSerializer
        return StyleBoardListSerializer

    def get_queryset(self):
        return StyleBoard.objects.filter(user=self.request.user)


class StyleBoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a style board."""

    serializer_class = StyleBoardDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.method == "GET":
            return StyleBoard.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            ).prefetch_related("outfits", "products")
        return StyleBoard.objects.filter(user=self.request.user)


class StyleBoardAddItemView(APIView):
    """Add an outfit or product to a style board."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            board = StyleBoard.objects.get(id=pk, user=request.user)
        except StyleBoard.DoesNotExist:
            return Response({"error": "Style board not found."}, status=status.HTTP_404_NOT_FOUND)

        outfit_id = request.data.get("outfit_id")
        product_id = request.data.get("product_id")

        if outfit_id:
            try:
                outfit = Outfit.objects.get(id=outfit_id)
                board.outfits.add(outfit)
            except Outfit.DoesNotExist:
                return Response({"error": "Outfit not found."}, status=status.HTTP_404_NOT_FOUND)

        if product_id:
            from apps.products.models import Product
            try:
                product = Product.objects.get(id=product_id, is_active=True)
                board.products.add(product)
            except Product.DoesNotExist:
                return Response({"error": "Product not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Item added to board."}, status=status.HTTP_200_OK)
