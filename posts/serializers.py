from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from accounts.serializers import ReadOnlyUserExternalSerializer
from comments.serializers import ReadOnlyCommentSerializer, ReplySerializer

from .models import Post


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
