from .converters import HandleConverter
from .views import (
    GetPresignedUrlView,
    PostViewSet,
    LatestPostsAPIView,
    LatestPostsViaHandleAPIView,
)
from django.urls import path, include, register_converter
from rest_framework.routers import DefaultRouter


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
