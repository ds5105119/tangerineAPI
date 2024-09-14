from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.response import Response

from api.permissions import UserReplyPermission
from posts.models import Post

from .models import Comment
from .serializers import CommentSerializer


class CommentListView(mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (UserReplyPermission,)

    def get_queryset(self):
        uuid = self.request.query_params.get("uuid")
        post = get_object_or_404(Post, uuid=uuid)
        return Comment.objects.filter(post=post).order_by("-created_at")

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class CommentUserViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    A Custom ViewSet that provides `create`, `list`, and `destory` actions.
    """

    permission_classes = (UserReplyPermission,)
    filter_backends = (DjangoFilterBackend,)
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filterset_fields = ["user", "content"]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
