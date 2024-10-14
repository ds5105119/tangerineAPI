from django.db.models import Exists, F, OuterRef, Prefetch
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status, viewsets
from rest_framework.pagination import CursorPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from comments.models import Comment, Reply
from follows.models import Follow
from likes.models import PostLike

from .apps import client, embedding_fn
from .models import Post, PostHistory, TaggedPost
from .permissions import PostPermissions
from .serializers import PostSerializer


class UserPostPagination(CursorPagination):
    """
    Pagination for UserViewSet
    """

    page_size = 10
    ordering = "-created_at"
    page_size_query_param = None
    max_page_size = 10


class LatestPostsViaHandleAPIView(generics.ListAPIView):
    """
    POST /posts/latest/{handle}: 유저 핸들로 얻는 최신 포스팅 리스트
    /posts/latest/{handle}/?cursor=xxx: 페이지네이션 기본 적용
    """

    permission_classes = (AllowAny,)
    serializer_class = PostSerializer
    pagination_class = UserPostPagination

    def get_queryset(self):
        handle = self.kwargs.get("handle")
        user = get_object_or_404(User, handle=handle)

        if user.is_authenticated:
            likes_exists = PostLike.objects.filter(post=OuterRef("pk"), like_user=user)
        else:
            likes_exists = PostLike.objects.none()

        return (
            Post.public_objects.filter(user=user)
            .select_related("user", "category")
            .prefetch_related(
                Prefetch(
                    "comments_post",
                    queryset=Comment.objects.select_related("user").prefetch_related(
                        Prefetch("replies_comment", queryset=Reply.objects.select_related("user")[:1], to_attr="reply")
                    )[:2],
                    to_attr="first_two_comments",
                )
            )
            .annotate(is_liked=Exists(likes_exists))
        )


class LatestPostsViaFollowAPIView(mixins.ListModelMixin, viewsets.GenericViewSet):
    """
    POST /posts/follows/{handle}: 유저가 팔로우한 사람의 포스팅 리스트
    /posts/follows/{handle}/?cursor=xxx: 페이지네이션 기본 적용
    """

    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer
    pagination_class = UserPostPagination

    def get_queryset(self):
        user = self.request.user
        follows = Follow.objects.filter(follower=user).values_list("user_id", flat=True)
        likes_exists = PostLike.objects.filter(post=OuterRef("pk"), like_user=user)
        return (
            Post.public_objects.filter(user__in=follows)
            .select_related("user", "category")
            .prefetch_related(
                Prefetch(
                    "comments_post",
                    queryset=Comment.objects.select_related("user").prefetch_related(
                        Prefetch("replies_comment", queryset=Reply.objects.select_related("user")[:1], to_attr="reply")
                    )[:2],
                    to_attr="first_two_comments",
                )
            )
            .annotate(is_liked=Exists(likes_exists))
        )


class RecommendPostsAPIView(generics.ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostSerializer


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    POST /post/p/: Create a new post via data
    GET /post/p/{uuid}: Get post[uuid] detail
    PUT /post/p/{uuid}: Update post[uuid]
    DELETE /post/p/{uuid}: Delete post[uuid]
    """

    permission_classes = (PostPermissions,)
    serializer_class = PostSerializer
    queryset = Post.objects.all()
    lookup_field = "uuid"

    def get_queryset(self):
        queryset = super().get_queryset()

        if self.action == "list":
            search_query = self.request.query_params.get("search", None)
            tags_query = self.request.query_params.get("tags", None)

            if search_query:
                post_uuid_milvus = client.search(
                    data=embedding_fn.encode_documents([search_query]),
                    anns_field="vector",
                    output_fields=["pk"],
                    limit=300,
                    param={},
                )
                post_uuid = [r.id for r in post_uuid_milvus[0]]
                queryset = queryset.filter(uuid__in=post_uuid)

            elif tags_query:
                queryset = queryset.filter(tags__icontains=tags_query)

            else:
                histories = PostHistory.objects.filter(user=self.request.user).select_related("post")[:30]

                if histories:
                    post_texts = [str(history.post.text) for history in histories]
                    post_uuid_milvus = client.search(
                        data=embedding_fn.encode_documents(post_texts),
                        anns_field="vector",
                        output_fields=["pk"],
                        limit=300,
                        param={},
                    )
                    post_uuid = [r.id for r in post_uuid_milvus[0]]
                    queryset = queryset.filter(uuid__in=post_uuid)

        elif self.action in ["retrieve", "list"]:
            likes_exists = PostLike.objects.filter(post=OuterRef("pk"), like_user=self.request.user)
            queryset = (
                queryset.select_related("user", "category")
                .prefetch_related(
                    Prefetch(
                        "comments_post",
                        queryset=Comment.objects.select_related("user").prefetch_related(
                            Prefetch(
                                "replies_comment", queryset=Reply.objects.select_related("user")[:1], to_attr="reply"
                            )
                        )[:2],
                        to_attr="first_two_comments",
                    )
                )
                .annotate(is_liked=Exists(likes_exists))
            )

        return queryset

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)

        uuid_string = str(post.uuid)
        text_string = str(post.text)
        tags_list = list(self.request.data.get("tags", ""))

        tagged_posts = [TaggedPost(post=post, tag=tag) for tag in tags_list]
        TaggedPost.objects.bulk_create(tagged_posts)

        vectors = embedding_fn.encode_documents([text_string])
        client.insert([{"pk": uuid_string, "vector": vectors[0]}])
        client.flush()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        PostHistory.objects.create(user=self.request.user, post=instance)
        Post.objects.filter(uuid=instance.uuid).update(views_count=F("views_count") + 1)
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
