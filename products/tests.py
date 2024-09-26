import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product
from products.serializers import ProductCreateUpdateSerializer, ProductRetrieveSerializer
from profiles.models import Profile


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    profile = Profile.objects.create(bio="test", link_1="test", link_2="test")

    return User.objects.create_user(
        username="testuser", email="testuser@gmail.com", handle="testhandle", profile=profile
    )


@pytest.fixture
def product(user):
    return Product.objects.create(
        user=user,
        name="Test Product",
        price=100,
        product_image_link="https://example.com/product-image.jpg",
        product_link="https://example.com/product",
    )


@pytest.mark.django_db
class TestProductModel:
    def test_product_creation(self, product):
        assert isinstance(product, Product)
        assert product.name == "Test Product"
        assert product.price == 100
        assert product.product_image_link == "https://example.com/product-image.jpg"
        assert product.product_link == "https://example.com/product"

    def test_product_str_representation(self, product):
        assert str(product) == "Test Product"


@pytest.mark.django_db
class TestProductSerializer:
    def test_product_retrieve_serializer(self, product):
        serializer = ProductRetrieveSerializer(product)
        assert "uuid" in serializer.data
        assert serializer.data["name"] == "Test Product"
        assert serializer.data["price"] == 100

    def test_product_create_update_serializer(self, user):
        data = {
            "user": {"handle": user.handle},
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


@pytest.mark.django_db
class TestProductViews:
    def test_create_product(self, api_client, user):
        api_client.force_authenticate(user=user)
        url = reverse("product-list")
        data = {
            "user": {"handle": user.handle},
            "name": "Test Product",
            "price": 150,
            "product_image_link": "https://example.com/api-test-product-image.jpg",
            "product_link": "https://example.com/api-test-product",
        }
        response = api_client.post(url, data, format="json")

        print(response.json())

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["user"] == {"handle": user.handle}
        assert response.data["name"] == "Test Product"
        assert response.data["price"] == 150
        assert response.data["product_image_link"] == "https://example.com/api-test-product-image.jpg"
        assert response.data["product_link"] == "https://example.com/api-test-product"

    def test_retrieve_product(self, api_client, product):
        url = reverse("product-detail", kwargs={"uuid": str(product.uuid)})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == product.name

    def test_update_product(self, api_client, product, user):
        api_client.force_authenticate(user=user)
        url = reverse("product-detail", kwargs={"uuid": str(product.uuid)})
        data = {"name": "Updated Product", "price": 300}
        response = api_client.patch(url, data)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Updated Product"
        assert response.data["price"] == 300

    def test_delete_product(self, api_client, product, user):
        api_client.force_authenticate(user=user)
        url = reverse("product-detail", kwargs={"uuid": str(product.uuid)})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_list_latest_products(self, api_client, user, product):
        url = reverse("user-latest-products", kwargs={"handle": user.handle})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0


@pytest.mark.django_db
class TestProductPermissions:
    def test_unauthenticated_user_cannot_create_product(self, api_client):
        """
        Test that products cannot be created if the user is not logged in or is not authenticated
        """
        url = reverse("product-list")
        data = {
            "name": "Unauthorized Product",
            "price": 100,
            "product_imege_link": "https://example.com/unauthorized-image.jpg",
            "product_link": "https://example.com/unauthorized",
        }
        response = api_client.post(url, data)
        print(response.json())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_owner_cannot_update_product(self, api_client, product):
        """
        Test that products cannot be modified by users when they are not logged in or are not authenticated
        """
        profile = Profile.objects.create(bio="otheruser", link_1="otheruser", link_2="otheruser")
        other_user = User.objects.create_user(
            username="otheruser", email="otheruser@test.com", handle="otheruser", profile=profile
        )
        api_client.force_authenticate(user=other_user)
        url = reverse("product-detail", kwargs={"uuid": product.uuid})
        data = {"name": "Unauthorized Update"}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
