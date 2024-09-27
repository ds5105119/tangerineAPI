from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CommentLikeViewSet, PostLikeViewSet, ReplyLikeViewSet

router = DefaultRouter()
router.register(r"post-likes", PostLikeViewSet)
router.register(r"comment-likes", CommentLikeViewSet)
router.register(r"reply-likes", ReplyLikeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
