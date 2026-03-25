"""
Review views for product reviews, ratings, and helpfulness.
"""

from django.db.models import Count, Q
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Review, ReviewHelpful
from .serializers import ReviewSerializer, ReviewCreateSerializer, ReviewStatsSerializer


class ReviewListView(generics.ListAPIView):
    """
    List reviews for a specific product.
    Filter by ?product=<uuid>
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        queryset = Review.objects.filter(is_approved=True).select_related("user").prefetch_related("images")
        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        # Sorting
        sort = self.request.query_params.get("sort", "newest")
        if sort == "highest":
            queryset = queryset.order_by("-rating", "-created_at")
        elif sort == "lowest":
            queryset = queryset.order_by("rating", "-created_at")
        elif sort == "helpful":
            queryset = queryset.order_by("-helpful_count", "-created_at")
        else:
            queryset = queryset.order_by("-created_at")

        return queryset


class ReviewCreateView(generics.CreateAPIView):
    """Create a new product review."""

    serializer_class = ReviewCreateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        return Response(
            ReviewSerializer(review, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class ReviewHelpfulView(APIView):
    """Mark a review as helpful (toggle)."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            review = Review.objects.get(id=pk, is_approved=True)
        except Review.DoesNotExist:
            return Response({"error": "Review not found."}, status=status.HTTP_404_NOT_FOUND)

        helpful, created = ReviewHelpful.objects.get_or_create(
            review=review, user=request.user
        )

        if not created:
            helpful.delete()
            review.helpful_count = max(0, review.helpful_count - 1)
            review.save(update_fields=["helpful_count"])
            return Response({"helpful": False, "helpful_count": review.helpful_count})

        review.helpful_count += 1
        review.save(update_fields=["helpful_count"])
        return Response({"helpful": True, "helpful_count": review.helpful_count})


class ReviewStatsView(APIView):
    """Get aggregated review statistics for a product."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        reviews = Review.objects.filter(product_id=product_id, is_approved=True)

        total = reviews.count()
        if total == 0:
            return Response({
                "average_rating": 0,
                "total_reviews": 0,
                "rating_distribution": {str(i): 0 for i in range(1, 6)},
                "fit_distribution": {"runs_small": 0, "true_to_size": 0, "runs_large": 0},
                "recommendation_percentage": 0,
            })

        # Rating distribution
        rating_dist = {}
        for i in range(1, 6):
            rating_dist[str(i)] = reviews.filter(rating=i).count()

        # Fit distribution
        fit_reviews = reviews.exclude(fit="")
        fit_total = fit_reviews.count()
        fit_dist = {
            "runs_small": fit_reviews.filter(fit="runs_small").count(),
            "true_to_size": fit_reviews.filter(fit="true_to_size").count(),
            "runs_large": fit_reviews.filter(fit="runs_large").count(),
        }

        # Average and recommendation
        avg_rating = sum(int(k) * v for k, v in rating_dist.items()) / total
        recommend_pct = (reviews.filter(would_recommend=True).count() / total) * 100

        data = {
            "average_rating": round(avg_rating, 2),
            "total_reviews": total,
            "rating_distribution": rating_dist,
            "fit_distribution": fit_dist,
            "recommendation_percentage": round(recommend_pct, 1),
        }

        serializer = ReviewStatsSerializer(data)
        return Response(serializer.data)
