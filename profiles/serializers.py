from profiles.models import Profile

try:
    from rest_framework import serializers
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class ProfileSelfSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "bio",
            "link_1",
            "link_2",
            "profile_image",
        )


class ProfileExternalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = (
            "bio",
            "link_1",
            "link_2",
            "profile_image",
        )
