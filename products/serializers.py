from django.conf import settings
from rest_framework import serializers

from .models import Product


class UserSerializer(serializers.Serializer):
    """
    User Serializer for handling user data in Product.
    """

    handle = serializers.CharField()


class ProductBaseSerializer(serializers.ModelSerializer):
    """
    Base Product Serializer for common fields.
    """

    user = UserSerializer()

    class Meta:
        model = Product
        fields = [
            "uuid",
            "user",
            "name",
            "price",
            "product_image_link",
            "product_link",
            "created_at",
        ]

    def validate_user(self, value):
        """
        Validate user information.
        """
        if not value.get("handle"):
            raise serializers.ValidationError("User handle is required.")
        return value


class ProductRetrieveSerializer(ProductBaseSerializer):
    """
    Serializer for retrieving product details.
    """

    pass


class ProductCreateUpdateSerializer(ProductBaseSerializer):
    """
    Serializer for creating and updating products.
    """

    class Meta(ProductBaseSerializer.Meta):
        read_only_fields = ["uuid", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Create a new product instance.
        """
        user_data = validated_data.pop("user", None)
        product = Product(**validated_data)

        if user_data:
            self._assign_user(product, user_data)

        product.save()
        return product

    def update(self, instance, validated_data):
        """
        Update an existing product instance.
        """
        user_data = validated_data.pop("user", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if user_data:
            self._assign_user(instance, user_data)

        product_link = validated_data.get("product_link", instance.product_link)
        if Product.objects.filter(product_link=product_link).exclude(uuid=instance.uuid).exists():
            raise serializers.ValidationError({"product_link": "This product is being posted."})

        instance.save()
        return instance

    def _assign_user(self, product_instance, user_data):
        """
        Helper method to assign user based on handle.
        """
        try:
            user = settings.AUTH_USER_MODEL.objects.get(handle=user_data["handle"])
            product_instance.user = user
        except settings.AUTH_USER_MODEL.DoesNotExist:
            raise serializers.ValidationError({"user": "User with this handle does not exist."})

    def validate(self, attrs):
        """
        Custom validation for create and update actions.
        """
        price = attrs.get("price", 0)
        if price < 0:
            raise serializers.ValidationError({"price": "Price must be a non-negative integer."})

        product_link = attrs.get("product_link")
        if Product.objects.filter(product_link=product_link).exists():
            raise serializers.ValidationError({"product_link": "This product is being posted."})

        return super().validate(attrs)
