import pytest
from django.db.models import Exists, OuterRef
from django.urls import reverse
from rest_framework import status

from likes.models import PostLike
from posts.models import Category, Post
from posts.serializers import PostSerializer

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_post_creation(self, sample_post):
        assert isinstance(sample_post, Post)
        assert sample_post.text == "Test Post"
        assert sample_post.status == "published"
        assert sample_post.views_count == 0
        assert sample_post.likes_count == 0

    def test_post_str_representation(self, sample_post):
        assert str(sample_post) == "Test Post"


class TestPostSerializer:
    def test_post_serializer(self, sample_post, sample_user_1):
        # Annotate the is_liked field
        post_with_is_liked = Post.objects.annotate(
            is_liked=Exists(PostLike.objects.filter(post=OuterRef("pk"), like_user=sample_user_1))
        ).get(pk=sample_post.pk)

        serializer = PostSerializer(post_with_is_liked)
        assert "uuid" in serializer.data
        assert serializer.data["text"] == "Test Post"
        assert serializer.data["user"]["handle"] == sample_user_1.handle
        assert "category" in serializer.data
        assert "comments" in serializer.data
        assert "is_liked" in serializer.data

    def test_post_create_serializer(self, sample_user_1, rf):
        data = {
            "text": "New Post",
            "category": "Test Category",
            "tags": ["tag1", "tag2"],
            "images": ["https://example.com/image1.jpg", "https://example.com/image2.jpg"],
        }
        request = rf.post("/fake-url/")
        request.user = sample_user_1
        serializer = PostSerializer(data=data, context={"request": request})
        assert serializer.is_valid(), serializer.errors
        post = serializer.save()
        assert post.text == "New Post"
        assert post.category.name == "Test Category"
        assert post.tags == ["tag1", "tag2"]
        assert post.images == ["https://example.com/image1.jpg", "https://example.com/image2.jpg"]
        assert post.user == sample_user_1


class TestPostViews:
    def test_create_post(self, client_1, sample_user_1):
        client_1.force_authenticate(user=sample_user_1)
        url = reverse("post-list")
        data = {
            "text": "Test Post",
            "category": "Test Category",
            "tags": ["tag1", "tag2"],
            "images": ["https://example.com/image1.jpg"],
        }
        response = client_1.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["text"] == "Test Post"
        assert response.data["category"] == "Test Category"
        assert response.data["tags"] == ["tag1", "tag2"]
        assert response.data["images"] == ["https://example.com/image1.jpg"]

    def test_retrieve_post(self, client_1, sample_post, sample_user_1):
        client_1.force_authenticate(user=sample_user_1)
        url = reverse("post-detail", kwargs={"uuid": str(sample_post.uuid)})
        response = client_1.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["text"] == sample_post.text
        assert "is_liked" in response.data

    def test_update_post(self, client_1, sample_post, sample_user_1):
        client_1.force_authenticate(user=sample_user_1)
        url = reverse("post-detail", kwargs={"uuid": str(sample_post.uuid)})
        data = {"text": "Updated Post", "category": "Updated Category"}
        response = client_1.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["text"] == "Updated Post"
        assert response.data["category"] == "Updated Category"

    def test_delete_post(self, client_1, sample_post, sample_user_1):
        client_1.force_authenticate(user=sample_user_1)
        url = reverse("post-detail", kwargs={"uuid": str(sample_post.uuid)})
        response = client_1.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_list_latest_posts(self, client_1, sample_user_1, sample_post):
        url = reverse("user-latest-posts", kwargs={"handle": sample_user_1.handle})
        response = client_1.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) > 0
        assert "is_liked" in response.data["results"][0]


class TestPostPermissions:
    def test_unauthenticated_user_cannot_create_post(self, client_1):
        url = reverse("post-list")
        data = {
            "text": "Unauthorized Post",
            "category": "Test Category",
            "tags": ["tag1", "tag2"],
            "images": ["https://example.com/image1.jpg"],
        }
        response = client_1.post(url, data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_non_owner_cannot_update_post(self, client_1, sample_post, sample_user_2):
        client_1.force_authenticate(user=sample_user_2)
        url = reverse("post-detail", kwargs={"uuid": str(sample_post.uuid)})
        data = {"text": "Unauthorized Update"}
        response = client_1.patch(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.fixture
def sample_post(sample_user_1):
    category = Category.objects.create(user=sample_user_1, name="Test Category")
    return Post.objects.create(
        user=sample_user_1,
        category=category,
        text="Test Post",
        tags=["tag1", "tag2"],
        images=["https://example.com/image1.jpg"],
    )
