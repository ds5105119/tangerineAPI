import uuid

from django.conf import settings
from django.db import models


class Report(models.Model):
    REPORT_CHOICES = [
        ("user", "User"),
        ("post", "Post"),
        ("comment", "Comment"),
        ("product", "Product"),
        ("chat", "Chat"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reporter")
    target_type = models.CharField(max_length=20, choices=REPORT_CHOICES)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="reported_user"
    )
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        verbose_name = "report"
        verbose_name_plural = "Reports"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} reports {self.target_type} ID {self.target_user}"
