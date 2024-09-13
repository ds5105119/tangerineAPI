from .models import Comment, Reply
from accounts.serializers import UserSerializer
from rest_framework import serializers
from posts.serializers import PostSerializer
from django.contrib.auth import get_user_model
from posts.models import Post

User = get_user_model()


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source="user.handle", read_only=True)
    post = serializers.CharField(source="post.uuid", read_only=True)

    class Meta:
        model = Comment
        fields = ["content", "post", "user", "created_at"]
        read_only_fields = ["created_at", "post", "user"]

    def create(self, validated_data):
        post_uuid = self.context["request"].data.get("uuid")
        user = self.context["request"].user

        post = Post.objects.get(uuid=post_uuid)

        comment = Comment.objects.create(
            content=validated_data["content"], post=post, user=user
        )
        return comment


class ReplySerializer(serializers.ModelSerializer):
    comment = CommentSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = ["comment", "user", "content"]
