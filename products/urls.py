from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    LatestProductsViaHandleViewSet,
    ProductViewSet,
    RecommendProductsAPIView,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
    path("recommend/", RecommendProductsAPIView.as_view(), name="user-recommend-products"),
    re_path(
        r"latest/(?P<handle>[\w.]+)/",
        LatestProductsViaHandleViewSet.as_view({"get": "list"}),
        name="user-latest-products",
    ),
]
