from accounts.serializers import *
from follows.models import *

try:
    from django.contrib.auth import get_user_model
    from rest_framework import serializers
except ImportError:
    raise ImportError("django, django-rest-framework, dj-rest-accounts needs to be added to INSTALLED_APPS.")


User = get_user_model()


class WritableFollowSelfSerializer(serializers.ModelSerializer):
    handle = serializers.CharField()

    class Meta:
        model = Follow
        fields = ("handle",)


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
