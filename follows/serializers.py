from accounts.serializers import UserSerializer
from follows.models import Follow

try:
    from rest_framework import serializers
except ImportError:
    raise ImportError("django, django-rest-framework, dj-rest-accounts needs to be added to INSTALLED_APPS.")


class FollowSerializer(serializers.ModelSerializer):
    follower = UserSerializer()
    user = UserSerializer()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Follow
        fields = ("follower", "user", "created_at")


class FollowerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("follower", "created_at")
        read_only_fields = ["follower", "created_at"]


class FollowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ("user", "created_at")
        read_only_fields = ["user", "created_at"]
