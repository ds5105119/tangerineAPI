from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    LatestPostsViaHandleAPIView,
    PostViewSet,
)

router = DefaultRouter()
router.register(r"p", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    re_path(
        r"latest/(?P<handle>[\w.]+)/",
        LatestPostsViaHandleAPIView.as_view(),
        name="user-latest-posts",
    ),
]
