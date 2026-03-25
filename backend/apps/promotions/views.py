"""
Promotion views for coupons, flash sales, and active promotions.
"""

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Promotion, Coupon, CouponUsage, FlashSale
from .serializers import (
    PromotionSerializer,
    CouponValidateSerializer,
    CouponResponseSerializer,
    FlashSaleListSerializer,
    FlashSaleDetailSerializer,
)


class ActivePromotionsView(generics.ListAPIView):
    """List currently active promotions."""

    serializer_class = PromotionSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        now = timezone.now()
        return Promotion.objects.filter(
            is_active=True, start_date__lte=now, end_date__gte=now,
        )


class CouponValidateView(APIView):
    """Validate a coupon code and calculate the discount."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CouponValidateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data["code"].strip().upper()
        subtotal = serializer.validated_data.get("subtotal", 0)

        try:
            coupon = Coupon.objects.get(code__iexact=code)
        except Coupon.DoesNotExist:
            return Response(
                {"valid": False, "message": "Invalid coupon code."},
                status=status.HTTP_200_OK,
            )

        if not coupon.is_valid:
            return Response(
                {"valid": False, "message": "This coupon has expired or is no longer available."},
                status=status.HTTP_200_OK,
            )

        # Check per-user usage limit
        user_usage_count = CouponUsage.objects.filter(
            coupon=coupon, user=request.user,
        ).count()
        if user_usage_count >= coupon.max_uses_per_user:
            return Response(
                {"valid": False, "message": "You have already used this coupon the maximum number of times."},
                status=status.HTTP_200_OK,
            )

        # Check minimum purchase
        if subtotal < coupon.min_purchase_amount:
            return Response(
                {
                    "valid": False,
                    "message": f"Minimum purchase of ${coupon.min_purchase_amount} required.",
                },
                status=status.HTTP_200_OK,
            )

        calculated_discount = coupon.calculate_discount(subtotal)

        response_data = {
            "valid": True,
            "code": coupon.code,
            "discount_type": coupon.discount_type,
            "discount_value": coupon.discount_value,
            "calculated_discount": calculated_discount,
            "min_purchase_amount": coupon.min_purchase_amount,
            "message": f"Coupon applied! You save ${calculated_discount}.",
        }

        return Response(CouponResponseSerializer(response_data).data, status=status.HTTP_200_OK)


class FlashSaleListView(generics.ListAPIView):
    """List active and upcoming flash sales."""

    serializer_class = FlashSaleListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        now = timezone.now()
        return FlashSale.objects.filter(
            is_active=True, end_time__gte=now,
        ).prefetch_related("products")


class FlashSaleDetailView(generics.RetrieveAPIView):
    """Retrieve flash sale detail with products."""

    serializer_class = FlashSaleDetailSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return FlashSale.objects.filter(is_active=True).prefetch_related(
            "products__images", "products__category",
        )
