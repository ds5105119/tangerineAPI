from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    """
    Product Model Serializer
    """

    user = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "uuid",
            "user",
            "name",
            "price",
            "product_link",
            "created_at",
        ]

    def get_user(self, obj):
        try:
            handle = obj.user.handle
            profile_image = (
                obj.user.profile.profile_image.url if obj.user.profile and obj.user.profile.profile_image else ""
            )
            return {
                "handle": handle,
                "profile_image": profile_image,
            }
        except AttributeError:
            return {
                "handle": "",
                "profile_image": "",
            }
