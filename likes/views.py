from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import Count, F
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    OpenApiTypes,
    extend_schema,
)
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from comments.models import Comment, Reply
from posts.models import Post

from .models import CommentLike, PostLike, ReplyLike
from .serializers import CommentLikeSerializer, PostLikeSerializer, ReplyLikeSerializer


class PostLikeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = PostLike.objects.all()
    serializer_class = PostLikeSerializer
    lookup_field = "uuid"
    lookup_value_regex = r"[0-9a-z\-]+"

    def get_queryset(self):
        uuid = self.request.query_params.get("uuid")
        if uuid:
            return PostLike.objects.filter(post__uuid=uuid)
        return PostLike.objects.none()

    @extend_schema(
        summary="Add like for a post",
        description="Like a post",
        parameters=[OpenApiParameter("uuid", description="Post UUID", required=True, type=OpenApiTypes.UUID)],
        responses={
            201: PostLikeSerializer,
            404: OpenApiResponse(description="Post not found"),
        },
    )
    def create(self, request, *args, **kwargs):
        uuid = self.request.query_params.get("uuid")
        try:
            post = Post.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if PostLike.objects.filter(post=post, like_user=user).exists():
            return Response({"detail": "Already liked"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            Post.objects.filter(uuid=uuid).update(likes_count=F("likes_count") + 1)
            serializer = self.get_serializer(data={"post_uuid": post.uuid, "like_user": user.id})
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        summary="Remove like for a post",
        description="Unlike a post",
        responses={
            204: OpenApiResponse(description="No content, like removed successfully"),
            404: OpenApiResponse(description="Post not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        try:
            post = Post.objects.get(uuid=self.kwargs.get("uuid"))
        except ObjectDoesNotExist:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        like = PostLike.objects.filter(post=post, like_user=user).first()

        if not like:
            return Response({"detail": "Not liked yet"}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            self.perform_destroy(like)
            Post.objects.filter(uuid=self.kwargs.get("uuid")).update(likes_count=F("likes_count") - 1)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Get users who liked a post",
        description="Retrieve a list of users who liked a specific post",
        parameters=[OpenApiParameter("uuid", description="Post UUID", required=True, type=OpenApiTypes.UUID)],
        responses={
            200: PostLikeSerializer(many=True),
            404: OpenApiResponse(description="Post not found"),
        },
    )
    def list(self, request, *args, **kwargs):
        uuid = self.request.query_params.get("uuid")
        try:
            post = Post.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            return Response({"detail": "Post not found"}, status=status.HTTP_404_NOT_FOUND)

        queryset = PostLike.objects.filter(post=post)
        serializer = self.get_serializer(queryset, many=True)

        return Response(serializer.data)


class CommentLikeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = CommentLike.objects.all()
    serializer_class = CommentLikeSerializer
    lookup_field = "uuid"
    lookup_value_regex = r"[0-9a-z\-]+"

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            uuid = self.request.query_params.get("uuid")
            if uuid:
                return CommentLike.objects.filter(comment__uuid=uuid)
            return CommentLike.objects.none()
        return CommentLike.objects.none()  # create(), destroy()일 때는 빈 쿼리셋

    @extend_schema(
        summary="Add like for a comment",
        description="Like a comment",
        parameters=[
            OpenApiParameter(
                "uuid",
                description="Comment UUID",
                required=True,
                type=OpenApiTypes.UUID,
            )
        ],
        responses={
            201: CommentLikeSerializer,
            404: OpenApiResponse(description="Comment not found"),
        },
    )
    def create(self, request, *args, **kwargs):
        uuid = self.request.query_params.get("uuid")
        try:
            comment = Comment.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if CommentLike.objects.filter(comment=comment, like_user=user).exists():
            return Response({"detail": "Already liked"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={"comment_uuid": comment.uuid, "like_user": user.handle})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        summary="Remove like for a comment",
        description="Unlike a comment",
        responses={
            204: OpenApiResponse(description="No content, like removed successfully"),
            404: OpenApiResponse(description="Comment not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        try:
            comment = Comment.objects.get(uuid=self.kwargs.get("uuid"))
        except ObjectDoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        like = CommentLike.objects.filter(comment=comment, like_user=user).first()

        if not like:
            return Response({"detail": "Not liked yet"}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(like)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Get users who liked a comment",
        description="Retrieve a list of users who liked a specific comment",
        parameters=[
            OpenApiParameter(
                "uuid",
                description="Comment UUID",
                required=True,
                type=OpenApiTypes.UUID,
            )
        ],
        responses={
            200: CommentLikeSerializer(many=True),
            404: OpenApiResponse(description="Comment not found"),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get like count for a comment",
        description="Retrieve the number of likes for a specific comment",
        responses={
            200: OpenApiTypes.INT,
            404: OpenApiResponse(description="Comment not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            comment = Comment.objects.annotate(like_count=Count("likes")).get(uuid=kwargs.get("uuid"))
            return Response({"like_count": comment.like_count}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"detail": "Comment not found"}, status=status.HTTP_404_NOT_FOUND)


class ReplyLikeViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = ReplyLike.objects.all()
    serializer_class = ReplyLikeSerializer
    lookup_field = "uuid"
    lookup_value_regex = r"[0-9a-z\-]+"

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            uuid = self.request.query_params.get("uuid")
            if uuid:
                return ReplyLike.objects.filter(reply__uuid=uuid)
            return ReplyLike.objects.none()
        return ReplyLike.objects.none()

    @extend_schema(
        summary="Add like for a reply",
        description="Like a reply",
        parameters=[OpenApiParameter("uuid", description="Reply UUID", required=True, type=OpenApiTypes.UUID)],
        responses={
            201: ReplyLikeSerializer,
            404: OpenApiResponse(description="Reply not found"),
        },
    )
    def create(self, request, *args, **kwargs):
        uuid = self.request.query_params.get("uuid")
        try:
            reply = Reply.objects.get(uuid=uuid)
        except ObjectDoesNotExist:
            return Response({"detail": "Reply not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if ReplyLike.objects.filter(reply=reply, like_user=user).exists():
            return Response({"detail": "Already liked"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data={"reply_uuid": reply.uuid, "like_user": user.handle})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(
        summary="Remove like for a reply",
        description="Unlike a reply",
        responses={
            204: OpenApiResponse(description="No content, like removed successfully"),
            404: OpenApiResponse(description="Reply not found"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        try:
            reply = Reply.objects.get(uuid=self.kwargs.get("uuid"))
        except ObjectDoesNotExist:
            return Response({"detail": "Reply not found"}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        like = ReplyLike.objects.filter(reply=reply, like_user=user).first()

        if not like:
            return Response({"detail": "Not liked yet"}, status=status.HTTP_400_BAD_REQUEST)

        self.perform_destroy(like)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        summary="Get users who liked a reply",
        description="Retrieve a list of users who liked a specific reply",
        parameters=[OpenApiParameter("uuid", description="Reply UUID", required=True, type=OpenApiTypes.UUID)],
        responses={
            200: ReplyLikeSerializer(many=True),
            404: OpenApiResponse(description="Reply not found"),
        },
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Get like count for a reply",
        description="Retrieve the number of likes for a specific reply",
        responses={
            200: OpenApiTypes.INT,
            404: OpenApiResponse(description="Reply not found"),
        },
    )
    def retrieve(self, request, *args, **kwargs):
        try:
            reply = Reply.objects.annotate(like_count=Count("likes")).get(uuid=kwargs.get("uuid"))
            return Response({"like_count": reply.like_count}, status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({"detail": "Reply not found"}, status=status.HTTP_404_NOT_FOUND)
