import uuid

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from comments.models import Comment, Reply
from likes.models import CommentLike, PostLike, ReplyLike
from likes.serializers import (
    CommentLikeSerializer,
    PostLikeSerializer,
    ReplyLikeSerializer,
)
from posts.models import Post
from profiles.models import Profile

User = get_user_model()


@pytest.fixture
def create_user_and_profile():
    def _create_user_and_profile(handle, username, email, password):
        profile = Profile.objects.create(
            bio="Test bio",
            link_1="http://test.com",
            link_2="http://test2.com",
            profile_image="http://test.com/image.png",
        )
        user = User.objects.create_user(
            handle=handle,
            username=username,
            email=email,
            password=password,
            profile=profile,
        )
        return user

    return _create_user_and_profile


@pytest.fixture
def post(db, user):
    """테스트용 게시물 생성"""
    return Post.objects.create(title="Test Post", content="Test Content", user=user)


# views.py


@pytest.mark.django_db
def test_post_like_create(create_user_and_profile):
    client = APIClient()

    # Create user and post
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    post = Post.objects.create(uuid=uuid.uuid4(), text="Test Post", likes_count=0, user=user)

    # Authenticate the request
    client.force_authenticate(user=user)

    # Like the post
    response = client.post(f"/likes/post-likes/?uuid={post.uuid}")

    post.refresh_from_db()  # Refresh to get the latest state from the database

    assert response.status_code == 201
    assert PostLike.objects.filter(post=post, like_user=user).exists()
    assert post.likes_count == 1  # Verify likes_count incremented


@pytest.mark.django_db
def test_post_like_destroy(create_user_and_profile):
    client = APIClient()

    # Create user, post, and like
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    post = Post.objects.create(uuid=uuid.uuid4(), text="Test Post", likes_count=1, user=user)
    PostLike.objects.create(post=post, like_user=user)

    # Authenticate the request
    client.force_authenticate(user=user)

    # Unlike the post
    response = client.delete(f"/likes/post-likes/{post.uuid}/")

    post.refresh_from_db()  # Refresh to get the latest state from the database

    assert response.status_code == 204
    assert not PostLike.objects.filter(post=post, like_user=user).exists()
    assert post.likes_count == 0  # Verify likes_count decremented


# PostLike list() test
@pytest.mark.django_db
def test_post_like_list(create_user_and_profile):
    client = APIClient()

    # Create user and post
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    post = Post.objects.create(uuid=uuid.uuid4(), text="Test Post", likes_count=0, user=user)

    # Authenticate the request
    client.force_authenticate(user=user)

    # Like the post
    PostLike.objects.create(post=post, like_user=user)

    # Get the list of users who liked the post
    response = client.get(f"/likes/post-likes/?uuid={post.uuid}")

    assert response.status_code == 200
    assert response.data[0]["like_user"] == user.handle  # Validate response data


@pytest.mark.django_db
def test_comment_like_create(create_user_and_profile):
    client = APIClient()

    # 사용자와 댓글 생성
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    comment = Comment.objects.create(
        uuid=uuid.uuid4(),
        content="Test Comment",
        user=user,
        post=Post.objects.create(user=user),
    )

    # 사용자 인증
    client.force_authenticate(user=user)

    # 댓글 좋아요 추가
    response = client.post(f"/likes/comment-likes/?uuid={comment.uuid}")

    assert response.status_code == 201
    assert CommentLike.objects.filter(comment=comment, like_user=user).exists()


@pytest.mark.django_db
def test_comment_like_destroy(create_user_and_profile):
    client = APIClient()

    # 사용자, 댓글, 좋아요 생성
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    comment = Comment.objects.create(
        uuid=uuid.uuid4(),
        content="Test Comment",
        user=user,
        post=Post.objects.create(user=user),
    )
    CommentLike.objects.create(comment=comment, like_user=user)

    # 사용자 인증
    client.force_authenticate(user=user)

    # 댓글 좋아요 제거
    response = client.delete(f"/likes/comment-likes/{comment.uuid}/")

    assert response.status_code == 204
    assert not CommentLike.objects.filter(comment=comment, like_user=user).exists()


@pytest.mark.django_db
def test_comment_like_list(create_user_and_profile):
    client = APIClient()

    # 사용자와 댓글 생성
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    comment = Comment.objects.create(
        uuid=uuid.uuid4(),
        content="Test Comment",
        user=user,
        post=Post.objects.create(user=user),
    )
    CommentLike.objects.create(comment=comment, like_user=user)

    # 사용자 인증
    client.force_authenticate(user=user)

    # 좋아요한 사용자 목록 가져오기
    response = client.get(f"/likes/comment-likes/?uuid={comment.uuid}")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["like_user"] == user.handle


@pytest.mark.django_db
def test_comment_like_retrieve(create_user_and_profile):
    client = APIClient()

    # Create user and comment like
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    comment = Comment.objects.create(
        uuid=uuid.uuid4(),
        content="Test Comment",
        user=user,
        post=Post.objects.create(user=user),
    )

    CommentLike.objects.create(comment=comment, like_user=user)

    # Authenticate the request
    client.force_authenticate(user=user)

    # Retrieve the like count for the comment
    response = client.get(f"/likes/comment-likes/{comment.uuid}/")

    assert response.status_code == 200
    assert response.data["like_count"] == 1  # Verify the correct like count


@pytest.mark.django_db
def test_reply_like_create(create_user_and_profile):
    client = APIClient()

    # 사용자와 답글 생성
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    reply = Reply.objects.create(
        uuid=uuid.uuid4(),
        content="Test Reply",
        user=user,
        comment=Comment.objects.create(user=user, post=Post.objects.create(user=user)),
    )

    # 사용자 인증
    client.force_authenticate(user=user)

    # 답글 좋아요 추가
    response = client.post(f"/likes/reply-likes/?uuid={reply.uuid}")

    assert response.status_code == 201
    assert ReplyLike.objects.filter(reply=reply, like_user=user).exists()


@pytest.mark.django_db
def test_reply_like_destroy(create_user_and_profile):
    client = APIClient()

    # 사용자, 답글, 좋아요 생성
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    reply = Reply.objects.create(
        uuid=uuid.uuid4(),
        content="Test Reply",
        user=user,
        comment=Comment.objects.create(user=user, post=Post.objects.create(user=user)),
    )
    ReplyLike.objects.create(reply=reply, like_user=user)

    # 사용자 인증
    client.force_authenticate(user=user)

    # 답글 좋아요 제거
    response = client.delete(f"/likes/reply-likes/{reply.uuid}/")

    assert response.status_code == 204
    assert not ReplyLike.objects.filter(reply=reply, like_user=user).exists()


@pytest.mark.django_db
def test_reply_like_list(create_user_and_profile):
    client = APIClient()

    # 사용자와 답글 생성
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    reply = Reply.objects.create(
        uuid=uuid.uuid4(),
        content="Test Reply",
        user=user,
        comment=Comment.objects.create(user=user, post=Post.objects.create(user=user)),
    )
    ReplyLike.objects.create(reply=reply, like_user=user)

    # 사용자 인증
    client.force_authenticate(user=user)

    # 좋아요한 사용자 목록 가져오기
    response = client.get(f"/likes/reply-likes/?uuid={reply.uuid}")

    assert response.status_code == 200
    assert len(response.data["results"]) == 1
    assert response.data["results"][0]["like_user"] == user.handle


@pytest.mark.django_db
def test_reply_like_retrieve(create_user_and_profile):
    client = APIClient()

    # Create user and reply like
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    reply = Reply.objects.create(
        uuid=uuid.uuid4(),
        content="Test Reply",
        user=user,
        comment=Comment.objects.create(user=user, post=Post.objects.create(user=user)),
    )

    ReplyLike.objects.create(reply=reply, like_user=user)

    # Authenticate the request
    client.force_authenticate(user=user)

    # Retrieve the like count for the reply
    response = client.get(f"/likes/reply-likes/{reply.uuid}/")

    assert response.status_code == 200
    assert response.data["like_count"] == 1  # Verify the correct like count


# models.py


@pytest.mark.django_db
def test_create_post_like(create_user_and_profile):
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    post = Post.objects.create(uuid=uuid.uuid4(), text="Test Post", likes_count=0, user=user)
    post_like = PostLike.objects.create(post=post, like_user=user)
    assert post_like.post == post
    assert post_like.like_user == user


@pytest.mark.django_db
def test_create_comment_like(create_user_and_profile):
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    comment = Comment.objects.create(
        uuid=uuid.uuid4(),
        content="Test Comment",
        user=user,
        post=Post.objects.create(user=user),
    )
    comment_like = CommentLike.objects.create(comment=comment, like_user=user)
    assert comment_like.comment == comment
    assert comment_like.like_user == user


@pytest.mark.django_db
def test_create_reply_like(create_user_and_profile):
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    reply = Reply.objects.create(
        uuid=uuid.uuid4(),
        content="Test Reply",
        user=user,
        comment=Comment.objects.create(user=user, post=Post.objects.create(user=user)),
    )
    reply_like = ReplyLike.objects.create(reply=reply, like_user=user)
    assert reply_like.reply == reply
    assert reply_like.like_user == user


# serializers.py


@pytest.mark.django_db
def test_post_like_serializer_valid(create_user_and_profile):
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    post = Post.objects.create(uuid=uuid.uuid4(), text="Test Content", user=user)
    data = {
        "post_uuid": str(post.uuid),
        "like_user": user.handle,
    }
    serializer = PostLikeSerializer(data=data, context={"request": user})

    assert serializer.is_valid(), f"Errors: {serializer.errors}"  # Provide error details if invalid
    post_like = serializer.save()

    assert post_like.post == post
    assert post_like.like_user == user


from rest_framework.test import APIRequestFactory


@pytest.mark.django_db
def test_comment_like_serializer_valid(create_user_and_profile):
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    comment = Comment.objects.create(
        uuid=uuid.uuid4(),
        content="Test Comment",
        user=user,
        post=Post.objects.create(user=user),
    )

    # APIRequestFactory를 사용해 request 객체 생성
    factory = APIRequestFactory()
    request = factory.post("/fake-url/")
    request.user = user  # request 객체에 user 추가

    data = {
        "comment_uuid": str(comment.uuid),
        "like_user": user.handle,
    }
    serializer = CommentLikeSerializer(data=data, context={"request": request})

    assert serializer.is_valid(), f"Errors: {serializer.errors}"  # 에러 디테일 제공
    comment_like = serializer.save()

    assert comment_like.comment == comment
    assert comment_like.like_user == user


@pytest.mark.django_db
def test_reply_like_serializer_valid(create_user_and_profile):
    user = create_user_and_profile("testuser", "Test User", "testuser@example.com", "password123")
    reply = Reply.objects.create(
        uuid=uuid.uuid4(),
        content="Test Reply",
        user=user,
        comment=Comment.objects.create(user=user, post=Post.objects.create(user=user)),
    )

    # APIRequestFactory를 사용해 request 객체 생성
    factory = APIRequestFactory()
    request = factory.post("/fake-url/")
    request.user = user  # request 객체에 user 추가

    data = {
        "reply_uuid": str(reply.uuid),
        "like_user": user.handle,
    }
    serializer = ReplyLikeSerializer(data=data, context={"request": request})

    assert serializer.is_valid(), f"Errors: {serializer.errors}"  # 에러 디테일 제공

    reply_like = serializer.save()

    assert reply_like.reply == reply
    assert reply_like.like_user == user
