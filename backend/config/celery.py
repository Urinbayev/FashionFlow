"""
Celery configuration for FashionFlow project.
"""

import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("fashionflow")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-flash-sale-expiry": {
        "task": "apps.promotions.tasks.deactivate_expired_flash_sales",
        "schedule": crontab(minute="*/5"),
    },
    "send-abandoned-cart-reminders": {
        "task": "apps.orders.tasks.send_abandoned_cart_reminders",
        "schedule": crontab(hour=10, minute=0),
    },
    "update-product-rankings": {
        "task": "apps.products.tasks.update_product_rankings",
        "schedule": crontab(hour=3, minute=0),
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task to verify Celery is working."""
    print(f"Request: {self.request!r}")
