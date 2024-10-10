from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    LatestProductsViaHandleViewSet,
    ProductViewSet,
    RecommendProductsViewSet,
)

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
router.register(r"recommend-products", RecommendProductsViewSet, basename="recommendproducts")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "latest/<handle>/",
        LatestProductsViaHandleViewSet.as_view({"get": "list"}),
        name="user-latest-products",
    ),
]
