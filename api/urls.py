from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("accounts/", include("accounts.urls")),
    path("chats/", include("chats.urls")),
    path("posts/", include("posts.urls")),
    path("images/", include("images.urls")),
    path("products/", include("products.urls")),
    path("follows/", include("follows.urls")),
    path("comments/", include("comments.urls")),
    path("likes/", include("likes.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
