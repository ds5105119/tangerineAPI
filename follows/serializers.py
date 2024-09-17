from accounts.serializers import *
from follows.models import *

try:
    from rest_framework import serializers
except ImportError:
    raise ImportError("django, django-rest-framework, dj-rest-accounts needs to be added to INSTALLED_APPS.")


class WritableFollowSelfSerializer(serializers.ModelSerializer):
    user = HandleOnlySerializer()

    class Meta:
        model = Follow
        fields = ("user",)

    def validate_user(self, value):
        try:
            user = User.objects.get(handle=value["handle"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this handle does not exist.")
        return user


class ReadOnlyFollowerExternalSerializer(serializers.ModelSerializer):
    follower = ReadOnlyUserExternalSerializer()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Follow
        fields = ("follower", "created_at")
        read_only_fields = ("follower", "created_at")


class ReadOnlyFollowingExternalSerializer(serializers.ModelSerializer):
    user = ReadOnlyUserExternalSerializer()
    created_at = serializers.DateTimeField()

    class Meta:
        model = Follow
        fields = ("user", "created_at")
        read_only_fields = ("user", "created_at")
