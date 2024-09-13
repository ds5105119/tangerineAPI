from comments.views import CommentListView
from django.urls import path, include
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register(r"", CommentListView)


urlpatterns = [
    path("", include(router.urls)),
]
