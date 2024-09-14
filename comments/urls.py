from django.urls import include, path
from rest_framework.routers import DefaultRouter

from comments.views import CommentListView

router = DefaultRouter()
router.register(r"", CommentListView)


urlpatterns = [
    path("", include(router.urls)),
]
