from rest_framework import serializers

from accounts.serializers import *
from comments.models import *


class CommentSerializer(serializers.ModelSerializer):
    user = ReadOnlyUserExternalSerializer(read_only=True)
    post = serializers.CharField(write_only=True)
    content = serializers.CharField()

    class Meta:
        model = Comment
        fields = ["content", "post", "user", "created_at"]
        read_only_fields = ["created_at", "user"]

    def validate_post(self, value):
        try:
            post_uuid = uuid.UUID(value)
        except ValueError:
            raise serializers.ValidationError("유효하지 않은 UUID입니다.")
        return post_uuid

    def create(self, validated_data):
        user = self.context["request"].user
        post_id = validated_data["post"]
        comment = Comment.objects.create(content=validated_data["content"], post_id=post_id, user=user)
        return comment


class ReplySerializer(serializers.ModelSerializer):
    comment = CommentSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = ["comment", "user", "content"]


class ReadOnlyCommentSerializer(serializers.ModelSerializer):
    user = ReadOnlyUserExternalSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["content", "user", "created_at"]
