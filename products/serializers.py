from rest_framework import serializers

from .models import Product


class ProductBaseSerializer(serializers.ModelSerializer):
    """
    Base Product Serializer for common fields.
    """

    class Meta:
        model = Product
        fields = [
            "uuid",
            # "user",
            "name",
            "price",
            "product_image_link",
            "product_link",
            "created_at",
        ]


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
        user = self.context["request"].user
        product = Product(**validated_data)
        product.user = user

        product.save()
        return product

    def update(self, instance, validated_data):
        """
        Update an existing product instance.
        """

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        product_link = validated_data.get("product_link", instance.product_link)
        if Product.objects.filter(product_link=product_link).exclude(uuid=instance.uuid).exists():
            raise serializers.ValidationError({"product_link": "This product is being posted."})

        instance.save()
        return instance

    def validate(self, attrs):
        """
        Custom validation for create and update actions.
        """
        price = attrs.get("price", 0)
        if price < 0:
            raise serializers.ValidationError({"price": "Price must be a non-negative integer."})

        return super().validate(attrs)
