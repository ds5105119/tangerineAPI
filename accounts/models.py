from accounts.managers import UserManager
from follows.models import Follow

try:
    from django.db import models
    from django.db.models import Subquery, OuterRef
    from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
except ImportError:
    raise ImportError("django needs to be added to INSTALLED_APPS.")


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that supports using email instead of username.
    password, last_login, is_active are defined by AbstractBaseUser
    is_superuser is defined by PermissionMixin
    """

    # User Field
    handle = models.CharField(max_length=30, unique=True, null=True, blank=False)
    username = models.CharField(max_length=30, null=False, blank=False)
    email = models.EmailField(max_length=30, unique=True, null=False, blank=False)

    # Manager Field
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    follows_count = models.IntegerField(default=0)
    followers_count = models.IntegerField(default=0)

    objects = UserManager()

    USERNAME_FIELD = "handle"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    class Meta:
        db_table = "user"
