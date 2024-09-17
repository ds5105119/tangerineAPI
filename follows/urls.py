from follows.views import FollowingViewSet

try:
    from django.urls import include, path
    from rest_framework.routers import DefaultRouter
except ImportError:
    raise ImportError("django needs to be added to INSTALLED_APPS.")


router = DefaultRouter()
router.register(r"", FollowingViewSet, basename="follow")


urlpatterns = [
    path(r"", include(router.urls), name="follows"),
]
