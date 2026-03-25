"""
Order views for order management, returns, and refunds.
"""

from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Order
from .serializers import (
    OrderCreateSerializer,
    OrderListSerializer,
    OrderDetailSerializer,
    ReturnCreateSerializer,
)
from .tasks import send_order_confirmation_email


class OrderCreateView(generics.CreateAPIView):
    """Create a new order from cart items."""

    serializer_class = OrderCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()

        # Trigger async email
        send_order_confirmation_email.delay(str(order.id))

        return Response(
            OrderDetailSerializer(order).data,
            status=status.HTTP_201_CREATED,
        )


class OrderListView(generics.ListAPIView):
    """List orders for the current user."""

    serializer_class = OrderListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related("items")


class OrderDetailView(generics.RetrieveAPIView):
    """Retrieve full order detail."""

    serializer_class = OrderDetailSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related(
            "items", "returns", "refunds",
        )


class OrderCancelView(APIView):
    """Cancel a pending or confirmed order."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status not in ("pending", "confirmed"):
            return Response(
                {"error": f"Cannot cancel an order with status '{order.get_status_display()}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Release reserved stock
        for item in order.items.select_related("variant"):
            variant = item.variant
            variant.reserved_stock = max(0, variant.reserved_stock - item.quantity)
            variant.save(update_fields=["reserved_stock"])

        order.status = "cancelled"
        order.cancelled_at = timezone.now()
        order.save(update_fields=["status", "cancelled_at", "updated_at"])

        return Response(
            {"message": "Order cancelled successfully.", "order": OrderDetailSerializer(order).data},
            status=status.HTTP_200_OK,
        )


class ReturnRequestView(APIView):
    """Create a return request for a delivered order."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if order.status != "delivered":
            return Response(
                {"error": "Returns can only be requested for delivered orders."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = ReturnCreateSerializer(
            data=request.data, context={"request": request, "order": order}
        )
        serializer.is_valid(raise_exception=True)
        return_request = serializer.save()

        return Response(
            {
                "message": "Return request submitted.",
                "return_id": str(return_request.id),
                "status": return_request.get_status_display(),
            },
            status=status.HTTP_201_CREATED,
        )
