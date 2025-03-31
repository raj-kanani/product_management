from datetime import timedelta

from celery import shared_task
from django.utils.timezone import now

from .models import Product


#Soft delete task
@shared_task
def soft_delete_products(product_ids):
    Product.objects.filter(id__in=product_ids).update(is_deleted=True, deleted_at=now())


@shared_task
def hard_delete_products():
    # set timezone using threshold
    threshold_time = now() - timedelta(hours=12)
    Product.objects.filter(is_deleted=True, deleted_at__lte=threshold_time).delete()
