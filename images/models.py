from django.conf import settings
from django.db import models

from posts.models import Post


class PresignedUrl(models.Model):
    url = models.CharField(max_length=500)
    is_public = models.BooleanField(default=False)


class PostImage(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="postimage")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postimage")
    url = models.URLField()
