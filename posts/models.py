import uuid

from django.conf import settings
from django.db import models

from .managers import PublishedManager


class TaggedPost(models.Model):
    tag = models.CharField(max_length=255)
    post = models.ForeignKey("Post", related_name="tagged_items", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Tagged Post"
        verbose_name_plural = "Tagged Posts"
        indexes = [models.Index(fields=["tag"])]
        constraints = [models.UniqueConstraint(fields=["tag", "post"], name="unique_tagged_posts")]


def get_undefined_category():
    """
    카테고리 외래 키가 삭제될 경우 호출되는 함수
    @return: undefined 이름의 카테고리
    """
    return Category.objects.get_or_create(name="undefined")


class Category(models.Model):
    """
    Custom Category model
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Post(models.Model):
    """
    Custom Posts model
    """

    POST_STATUS = [
        ("published", "Published"),
        ("suspended", "Suspended"),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts")
    category = models.ForeignKey(
        Category,
        on_delete=models.SET(get_undefined_category),
        null=True,
        related_name="posts",
    )
    status = models.CharField(max_length=10, choices=POST_STATUS, default="published")
    text = models.TextField()
    tags = models.TextField()
    images = models.JSONField(default=list, blank=True)
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    public_objects = PublishedManager()

    class Meta:
        verbose_name = "post"
        default_manager_name = "objects"
        ordering = ["-created_at"]

    def __str__(self):
        return self.text


class PostHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="history_user")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="history_post")
    created_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        verbose_name = "post_history"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user"])]
