from django.db import models


class PublishedManager(models.Manager):
    """
    Custom Django Model Manager for Posts model
    """
    def get_queryset(self):
        return super().get_queryset().filter(status='published')
