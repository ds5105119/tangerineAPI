from accounts.serializers import UserSelfSerializer, UserExternalSerializer
from profiles.models import Profile

try:
    from rest_framework import serializers
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class ProfileSelfSerializer(serializers.ModelSerializer):
    user = UserSelfSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "user",
            "bio",
            "link_1",
            "link_2",
            "profile_image",
        )


class ProfileExternalSerializer(serializers.ModelSerializer):
    user = UserExternalSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = (
            "user",
            "bio",
            "link_1",
            "link_2",
            "profile_image",
        )
