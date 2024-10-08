from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LatestProductsViaHandleViewSet,
    ProductViewSet,
    RecommendProductsAPIViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")

urlpatterns = [
    path("", include(router.urls)),
    path("recommend/", RecommendProductsAPIViewSet.as_view(), name="user-recommend-products"),
    path(
        "latest/<handle>/",
        LatestProductsViaHandleViewSet.as_view({"get": "list"}),
        name="user-latest-products",
    ),
]
