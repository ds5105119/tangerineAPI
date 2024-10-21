from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.serializers import ReadOnlyUserExternalSerializer
from comments.serializers import ReadOnlyCommentSerializer, ReplySerializer

from .models import Category, Post


class PostSerializer(serializers.ModelSerializer):
    """
    Post Model Serializer
    Django-taggit support
    """

    user = ReadOnlyUserExternalSerializer(read_only=True)
    category = serializers.CharField(required=False)
    images = serializers.ListField(child=serializers.URLField(), required=False)
    tags = serializers.ListField(child=serializers.CharField(), required=False)
    comments = serializers.SerializerMethodField(read_only=True)
    is_liked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        fields = [
            "uuid",
            "user",
            "category",
            "comments",
            "status",
            "images",
            "text",
            "tags",
            "views_count",
            "likes_count",
            "created_at",
            "is_liked",
        ]

        write_only_fields = ["tags"]
        read_only_fields = ["user", "status", "views_count", "likes_count", "created_at", "comments", "is_liked"]

    @extend_schema_field(ReadOnlyCommentSerializer(many=True))
    def get_comments(self, obj):
        comments = obj.first_two_comments if hasattr(obj, "first_two_comments") else obj.comments_post.all()[:2]
        comment_data = []
        for comment in comments:
            comment_serializer = ReadOnlyCommentSerializer(comment)
            comment_data.append(
                {
                    **comment_serializer.data,
                    "reply": ReplySerializer(comment.replies_comment.first()).data
                    if comment.replies_comment.exists()
                    else None,
                }
            )
        return comment_data

    def create(self, validated_data):
        category_name = validated_data.pop("category", None)
        user = self.context["request"].user

        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name, user=user)
            validated_data["category"] = category

        validated_data["user"] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        category_name = validated_data.pop("category", None)

        if category_name:
            category, _ = Category.objects.get_or_create(name=category_name, user=instance.user)
            validated_data["category"] = category

        return super().update(instance, validated_data)
