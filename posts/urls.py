from django.urls import include, path, register_converter
from rest_framework.routers import DefaultRouter

from .converters import HandleConverter
from .views import (
    GetPresignedUrlView,
    LatestPostsAPIView,
    LatestPostsViaHandleAPIView,
    PostViewSet,
)

register_converter(HandleConverter, "handle")
router = DefaultRouter()
router.register(r"p", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("presigned/", GetPresignedUrlView.as_view(), name="presigned"),
    path("latest/", LatestPostsAPIView.as_view(), name="latest"),
    path(
        "latest/<handle:handle>/",
        LatestPostsViaHandleAPIView.as_view(),
        name="user-latest-posts",
    ),
]
