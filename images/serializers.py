from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import PostImage

User = get_user_model()


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = [
            "user",
            "post",
            "url",
        ]
        read_only_fields = ["user"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
