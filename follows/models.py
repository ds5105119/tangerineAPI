from django.conf import settings

try:
    from django.db import models
except ImportError:
    raise ImportError("django needs to be added to INSTALLED_APPS.")


User = settings.AUTH_USER_MODEL


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following")
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name="followers")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "follow"
        constraints = [models.UniqueConstraint(fields=["user", "follower"], name="unique_followers")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.follower} follows {self.user}"
