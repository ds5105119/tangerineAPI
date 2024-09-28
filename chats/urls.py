from chats.views import *

try:
    from django.urls import include, path
    from rest_framework.routers import DefaultRouter
except ImportError:
    raise ImportError("django needs to be added to INSTALLED_APPS.")


router = DefaultRouter()
router.register(r"", ChatRoomViewSet, basename="follow")


urlpatterns = [
    path(r"rooms/", include(router.urls), name="follows"),
]
