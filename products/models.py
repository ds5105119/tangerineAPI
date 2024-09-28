import uuid

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

from .managers import PublishedManager


class Product(models.Model):
    """
    Custom Product model
    """

    POST_STATUS = [
        ("draft", "Draft"),
        ("published", "Published"),
        ("suspended", "Suspended"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="products")
    status = models.CharField(max_length=20, choices=POST_STATUS, default="published")
    product_nm = models.CharField(max_length=15, validators=[MinLengthValidator(2)])
    price = models.IntegerField(default=0)
    product_link = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    public_objects = PublishedManager()

    class Meta:
        verbose_name = "Product"
        verbose_name_plural = "Products"
        default_manager_name = "objects"
        ordering = ["-created_at", "status"]

    def __str__(self):
        return self.product_nm
