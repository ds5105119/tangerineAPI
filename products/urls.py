from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    LatestProductsViaHandleAPIView,
    ProductViewSet,
    RecommendProductsAPIView,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
urlpatterns = [
    path("", include(router.urls)),
    re_path(
        r"latest/(?P<handle>[\w.]+)/",
        LatestProductsViaHandleAPIView.as_view(),
        name="user-latest-products",
    ),
    re_path(
        r"recommend/(?P<handle>[\w.]+)/",
        RecommendProductsAPIView.as_view(),
        name="user-recommend-products",
    ),
]
