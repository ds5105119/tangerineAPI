from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import GetPrivatePresignedUrlView, GetPublicPresignedUrlView, PostImageViewSet

router = DefaultRouter()
router.register(r"posts/", PostImageViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("presigned/private/", GetPrivatePresignedUrlView.as_view(), name="presigned_private"),
    path("presigned/public/", GetPublicPresignedUrlView.as_view(), name="presigned_public"),
]
