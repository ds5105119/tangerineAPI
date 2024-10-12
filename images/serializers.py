from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostImage

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["handle"]


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = [
            "uuid",
            "user",
            "post",
            "url",
            "key",
            "content_type",
            "policy",
            "signature",
        ]
