import uuid

from django.conf import settings
from django.db import models

from posts.models import Post


class PostImage(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="postimage")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="postimage")
    url = models.URLField()
    key = models.CharField(max_length=255)
    content_type = models.CharField(max_length=50)
    policy = models.TextField()
    signature = models.CharField(max_length=255)
