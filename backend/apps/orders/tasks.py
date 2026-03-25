"""
Celery tasks for order processing.
"""

import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_order_confirmation_email(self, order_id):
    """Send order confirmation email to the customer."""
    from .models import Order

    try:
        order = Order.objects.select_related("user").prefetch_related("items").get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found for confirmation email.")
        return

    subject = f"FashionFlow - Order Confirmation #{order.order_number}"
    message = (
        f"Hi {order.user.first_name},\n\n"
        f"Thank you for your order #{order.order_number}!\n\n"
        f"Order Summary:\n"
    )

    for item in order.items.all():
        message += f"  - {item.product_name} ({item.color_name}, {item.size_name}) x{item.quantity} - ${item.line_total}\n"

    message += (
        f"\nSubtotal: ${order.subtotal}\n"
        f"Shipping: ${order.shipping_cost}\n"
        f"Tax: ${order.tax_amount}\n"
        f"Discount: -${order.discount_amount}\n"
        f"Total: ${order.total}\n\n"
        f"Shipping to: {order.shipping_name}, {order.shipping_address_1}, "
        f"{order.shipping_city}, {order.shipping_postal_code}\n\n"
        f"We'll send you another email when your order ships.\n\n"
        f"Thank you for shopping with FashionFlow!"
    )

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )
        logger.info(f"Order confirmation email sent for {order.order_number}.")
    except Exception as exc:
        logger.error(f"Failed to send order confirmation for {order.order_number}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_shipping_notification(self, order_id):
    """Send shipping notification email with tracking info."""
    from .models import Order

    try:
        order = Order.objects.select_related("user").get(id=order_id)
    except Order.DoesNotExist:
        logger.error(f"Order {order_id} not found for shipping notification.")
        return

    subject = f"FashionFlow - Your Order #{order.order_number} Has Shipped!"
    message = (
        f"Hi {order.user.first_name},\n\n"
        f"Great news! Your order #{order.order_number} is on its way.\n\n"
    )

    if order.tracking_number:
        message += f"Tracking Number: {order.tracking_number}\n"
    if order.tracking_url:
        message += f"Track your package: {order.tracking_url}\n"
    if order.estimated_delivery:
        message += f"Estimated Delivery: {order.estimated_delivery.strftime('%B %d, %Y')}\n"

    message += "\nThank you for shopping with FashionFlow!"

    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[order.user.email],
            fail_silently=False,
        )
        logger.info(f"Shipping notification sent for {order.order_number}.")
    except Exception as exc:
        logger.error(f"Failed to send shipping notification for {order.order_number}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def send_abandoned_cart_reminders():
    """
    Send email reminders for users who have pending orders
    that haven't been paid within 24 hours (abandoned carts).
    """
    from .models import Order

    cutoff = timezone.now() - timezone.timedelta(hours=24)
    abandoned_orders = Order.objects.filter(
        status="pending",
        payment_status="pending",
        created_at__lte=cutoff,
        created_at__gte=cutoff - timezone.timedelta(hours=24),
    ).select_related("user")

    sent_count = 0
    for order in abandoned_orders:
        subject = f"FashionFlow - Complete Your Order #{order.order_number}"
        message = (
            f"Hi {order.user.first_name},\n\n"
            f"Looks like you left some items in your cart. "
            f"Your order #{order.order_number} is still waiting for you.\n\n"
            f"Total: ${order.total}\n\n"
            f"Complete your purchase before the items sell out!\n\n"
            f"Thank you,\nFashionFlow Team"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                fail_silently=True,
            )
            sent_count += 1
        except Exception as exc:
            logger.error(f"Failed to send abandoned cart reminder for {order.order_number}: {exc}")

    logger.info(f"Sent {sent_count} abandoned cart reminders.")
    return sent_count
