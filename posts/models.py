import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import PublishedManager


class UUIDTaggedItem(models.Model):
    """
    for uuid pk field
    If you only inherit GenericUUIDTaggedItemBase, you need to define
    a tag field. e.g.
    tag = models.ForeignKey(Tag, related_name="uuid_tagged_items", on_delete=models.CASCADE)
    See https://django-taggit.readthedocs.io/en/latest/custom_tagging.html#genericuuidtaggeditembase
    """

    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")


def get_undefined_category():
    """
    Callback called by on_delete when the category foreign key of the posts is deleted
    :return: Category object named undefined
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
        ("draft", "Draft"),
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
    status = models.CharField(max_length=20, choices=POST_STATUS, default="published")
    mdx = models.TextField()
    text = models.TextField()
    tags = models.TextField()
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()
    public_objects = PublishedManager()

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        default_manager_name = "objects"
        ordering = [
            "-created_at",
        ]

    def __str__(self):
        return self.text
