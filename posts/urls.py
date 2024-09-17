from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    GetPresignedUrlView,
    LatestPostsAPIView,
    LatestPostsViaHandleAPIView,
    PostViewSet,
)

router = DefaultRouter()
router.register(r"p", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("presigned/", GetPresignedUrlView.as_view(), name="presigned"),
    path("latest/", LatestPostsAPIView.as_view(), name="latest"),
    re_path(
        r"latest/(?P<handle>[\w.]+)/",
        LatestPostsViaHandleAPIView.as_view(),
        name="user-latest-posts",
    ),
]
