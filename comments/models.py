import uuid

from django.conf import settings
from django.db import models

from posts.models import Post


class Comment(models.Model):
    """
    Custom Reply model
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    content = models.TextField()

    class Meta:
        verbose_name = "Comment"
        verbose_name_plural = "Comments"

    def __str__(self):
        return f"Comment by {self.user} on post {self.post}"


class Reply(models.Model):
    """
    Custom Reply model
    """

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="replies",
    )
    content = models.TextField()

    class Meta:
        verbose_name = "Reply"
        verbose_name_plural = "Replies"

    def __str__(self):
        return f"Reply by {self.user} on post {self.comment}"
