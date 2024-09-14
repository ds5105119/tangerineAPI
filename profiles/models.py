try:
    from django.conf import settings
    from django.db import models
except ImportError:
    raise ImportError("django needs to be added to INSTALLED_APPS.")


User = settings.AUTH_USER_MODEL


class Profile(models.Model):
    """
    Custom Profile model
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True, default="")
    link_1 = models.URLField(blank=True, default="")
    link_2 = models.URLField(blank=True, default="")
    profile_image = models.URLField(max_length=500, null=False, blank=True, default="")
