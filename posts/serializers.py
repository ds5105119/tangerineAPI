from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):
    """
    Post Model Serializer
    Django-taggit support
    """

    user = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "uuid",
            "user",
            "category",
            "status",
            "mdx",
            "text",
            "tags",
            "views_count",
            "likes_count",
            "created_at",
        ]

    def get_user(self, obj):
        return {
            "handle": obj.user.handle,
            "profile_image": (obj.user.profile.profile_image.url if obj.user.profile.profile_image else ""),
        }
