from .models import Post
from .serializers import PostSerializer
from .services import get_presigned_post
from .permissions import PostPermissions
from accounts.models import User

from django.db.models import F
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination


class UserPostPagination(PageNumberPagination):
    """
    Pagination for UserViewSet
    """

    page_size = 20
    page_size_query_param = None
    max_page_size = 20


class GetPresignedUrlView(APIView):
    """
    POST /posts/presigned/: get AWS S3 Bucket presigned post url
    """

    permission_classes = (IsAuthenticated,)
    throttle_scope = "GetPresignedUrlView"

    def post(self, request):
        try:
            presigned_url = get_presigned_post()
            return Response(presigned_url)
        except Exception as e:
            return Response({"error": str(e)})


class LatestPostsViaHandleAPIView(generics.ListAPIView):
    """
    POST /posts/latest/{handle}: return latest post via user
    /posts/latest/{handle}/?page=2: return latest post via user and pagination
    """

    permission_classes = (AllowAny,)
    serializer_class = PostSerializer
    pagination_class = UserPostPagination

    def get_queryset(self):
        handle = self.kwargs.get("handle")
        user = get_object_or_404(User, handle=handle)
        return Post.public_objects.filter(user=user).order_by("-created_at")


class LatestPostsAPIView(generics.ListAPIView):
    """
    POST /posts/latest/{handle}: return latest post via user
    /posts/latest/{handle}/?page=2: return latest post via user and pagination
    """

    permission_classes = (AllowAny,)
    serializer_class = PostSerializer
    pagination_class = UserPostPagination
    queryset = Post.objects.all()


class RecommendPostsAPIView(generics.ListAPIView):
    permission_classes = (AllowAny,)
    serializer_class = PostSerializer


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
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

    def perform_create(self, serializer):
        post = serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
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
