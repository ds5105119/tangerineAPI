from follows.views import FollowingViewSet

try:
    from django.urls import path, include
    from rest_framework.routers import DefaultRouter
except ImportError:
    raise ImportError("django needs to be added to INSTALLED_APPS.")


router = DefaultRouter()
router.register(r"follow", FollowingViewSet, basename="follow")


urlpatterns = [
    path(
        "",
        FollowingViewSet.as_view(
            {"get": "list", "post": "create", "delete": "destroy"}
        ),
        name="user_follow",
    ),
]
