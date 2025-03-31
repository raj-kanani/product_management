from django.db import models



class Product(models.Model):
    handle = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True, null=True)
    vendor = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    tags = models.TextField(blank=True, null=True)
    published = models.CharField(max_length=255)
    variant_sku = models.CharField(max_length=255)
    variant_inventory_tracker = models.CharField(max_length=255)
    variant_price = models.CharField(max_length=255)
    image_src = models.URLField(blank=True, null=True)
    is_deleted = models.BooleanField(default=False) #soft delete
    deleted_at = models.DateTimeField(blank=True, null=True)


    def __str__(self):
        return self.title
