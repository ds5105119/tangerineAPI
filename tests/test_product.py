import pytest
from django.urls import reverse
from rest_framework import status

from products.models import Product
from products.serializers import ProductCreateUpdateSerializer, ProductRetrieveSerializer

pytestmark = pytest.mark.django_db


class TestProductModel:
    def test_product_creation(self, sample_product):
        assert isinstance(sample_product, Product)
        assert sample_product.name == "Test Product"
        assert sample_product.price == 100
        assert sample_product.product_image_link == "https://example.com/product-image.jpg"
        assert sample_product.product_link == "https://example.com/product"

    def test_product_str_representation(self, sample_product):
        assert str(sample_product) == "Test Product"


class TestProductSerializer:
    def test_product_retrieve_serializer(self, sample_product):
        serializer = ProductRetrieveSerializer(sample_product)
        assert "uuid" in serializer.data
        assert serializer.data["name"] == "Test Product"
        assert serializer.data["price"] == 100

    def test_product_create_update_serializer(self, sample_user_1):
        data = {
            "user": {"handle": sample_user_1.handle},
            "name": "New Product",
            "price": 200,
            "product_image_link": "https://example.com/new-product-image.jpg",
            "product_link": "https://example.com/new-product",
        }
        serializer = ProductCreateUpdateSerializer(data=data)
        assert serializer.is_valid(), serializer.errors
        validated_data = serializer.validated_data
        assert validated_data["name"] == "New Product"
        assert validated_data["price"] == 200
        assert validated_data["product_image_link"] == "https://example.com/new-product-image.jpg"
        assert validated_data["product_link"] == "https://example.com/new-product"


class TestProductViews:
    def test_create_product(self, client_1, sample_user_1):
        client_1.force_authenticate(user=sample_user_1)
        url = reverse("product-list")
        data = {
            "user": {"handle": sample_user_1.handle},
            "name": "Test Product",
            "price": 150,
            "product_image_link": "https://example.com/api-test-product-image.jpg",
            "product_link": "https://example.com/api-test-product",
        }
        response = client_1.post(url, data, format="json")
        print(response.json())
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == "Test Product"
        assert response.data["price"] == 150
        assert response.data["product_image_link"] == "https://example.com/api-test-product-image.jpg"
        assert response.data["product_link"] == "https://example.com/api-test-product"

    def test_retrieve_product(self, client_1, sample_product):
        url = reverse("product-detail", kwargs={"uuid": str(sample_product.uuid)})
        response = client_1.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == sample_product.name

    def test_update_product(self, client_1, sample_product, sample_user_1):
        client_1.force_authenticate(user=sample_user_1)
        url = reverse("product-detail", kwargs={"uuid": str(sample_product.uuid)})
        data = {"name": "Updated Product", "price": 300}
        response = client_1.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Product"
        assert response.data["price"] == 300

    def test_delete_product(self, client_1, sample_product, sample_user_1):
        client_1.force_authenticate(user=sample_user_1)
        url = reverse("product-detail", kwargs={"uuid": str(sample_product.uuid)})
        response = client_1.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    # def test_list_latest_products(self, client_1, sample_user_1, sample_product):
    #     url = reverse("user-latest-products", kwargs={"handle": sample_user_1.handle})
    #     response = client_1.get(url)
    #     assert response.status_code == status.HTTP_200_OK
    #     assert len(response.data["results"]) > 0


class TestProductPermissions:
    def test_unauthenticated_user_cannot_create_product(self, client_1):
        """
        Test that products cannot be created if the user is not logged in or is not authenticated
        """
        url = reverse("product-list")
        data = {
            "name": "Unauthorized Product",
            "price": 100,
            "product_image_link": "https://example.com/unauthorized-image.jpg",
            "product_link": "https://example.com/unauthorized",
        }
        response = client_1.post(url, data)
        print(response.json())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # def test_non_owner_cannot_update_product(self, client_1, sample_product):
    #     """
    #     Test that products cannot be modified by users when they are not logged in or are not authenticated
    #     """
    #     client_1.force_authenticate(user=sample_user_1)
    #     url = reverse("product-detail", kwargs={"uuid": sample_product.uuid})
    #     data = {"name": "Unauthorized Update"}
    #     response = client_1.patch(url, data)
    #     assert response.status_code == status.HTTP_403_FORBIDDEN
