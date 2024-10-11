from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import PostImageViewSet

router = DefaultRouter()
router.register(r"post-images", PostImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
