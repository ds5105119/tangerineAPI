import pytest
from rest_framework.test import APIClient

from accounts.models import User
from products.models import Product
from profiles.models import Profile


@pytest.fixture
def create_sample_user():
    def _create_sample_user(username, bio, link):
        profile = Profile.objects.create(bio=bio, link_1=link, link_2=link)
        return User.objects.create_user(
            username=username, email=f"{username}@gmail.com", handle=username, profile=profile
        )

    return _create_sample_user


@pytest.fixture
def sample_user_1(create_sample_user):
    return create_sample_user("sample_user_1", "user_1", "user_1")


@pytest.fixture
def sample_user_2(create_sample_user):
    return create_sample_user("sample_user_2", "user_2", "user_2")


@pytest.fixture
def sample_user_3(create_sample_user):
    return create_sample_user("sample_user_3", "user_3", "user_3")


@pytest.fixture(params=["sample_user_1", "sample_user_2", "sample_user_3"])
def client(request):
    user = request.getfixturevalue(request.param)  # Get the user fixture dynamically
    client = APIClient()
    client.force_login(user)
    return client


@pytest.fixture
def client_1(sample_user_1):
    client = APIClient()
    client.force_login(sample_user_1)
    return client


@pytest.fixture
def client_2(sample_user_2):
    client = APIClient()
    client.force_login(sample_user_2)
    return client


@pytest.fixture
def client_3(sample_user_3):
    client = APIClient()
    client.force_login(sample_user_3)
    return client


@pytest.fixture
def sample_product(sample_user_1):
    return Product.objects.create(
        user=sample_user_1,
        name="Test Product",
        price=100,
        product_image_link="https://example.com/product-image.jpg",
        product_link="https://example.com/product",
    )
