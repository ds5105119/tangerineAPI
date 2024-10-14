from django.contrib.auth import get_user_model
from rest_framework import serializers

from accounts.serializers import ReadOnlyUserExternalSerializer
from comments.models import Comment, Reply
from posts.models import Post

from .models import CommentLike, PostLike, ReplyLike

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["handle"]


class PostLikeSerializer(serializers.ModelSerializer):
    post_uuid = serializers.UUIDField(write_only=True)

    class Meta:
        model = PostLike
        fields = ["post_uuid", "like_user"]
        read_only_fields = ["like_user"]

    def create(self, validated_data):
        post_uuid = validated_data.pop("post_uuid")
        post = Post.objects.get(uuid=post_uuid)

        validated_data["post"] = post
        validated_data["like_user"] = self.context["request"].user

        return super().create(validated_data)


class ReadonlyPostLikeSerializer(serializers.ModelSerializer):
    like_user = ReadOnlyUserExternalSerializer(read_only=True)

    class Meta:
        model = PostLike
        fields = ["like_user"]


class CommentLikeSerializer(serializers.ModelSerializer):
    comment_uuid = serializers.UUIDField(write_only=True)
    like_user = serializers.CharField(read_only=True)

    class Meta:
        model = CommentLike
        fields = ["comment_uuid", "like_user", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        comment_uuid = validated_data.pop("comment_uuid")
        comment = Comment.objects.get(uuid=comment_uuid)
        validated_data["comment"] = comment
        validated_data["like_user"] = self.context["request"].user
        return super().create(validated_data)


class ReplyLikeSerializer(serializers.ModelSerializer):
    reply_uuid = serializers.UUIDField(write_only=True)
    like_user = serializers.CharField(read_only=True)

    class Meta:
        model = ReplyLike
        fields = ["reply_uuid", "like_user", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        reply_uuid = validated_data.pop("reply_uuid")
        reply = Reply.objects.get(uuid=reply_uuid)
        validated_data["reply"] = reply
        validated_data["like_user"] = self.context["request"].user
        return super().create(validated_data)
