from chats.views import *

try:
    from django.urls import include, path
    from rest_framework.routers import DefaultRouter
except ImportError:
    raise ImportError("django needs to be added to INSTALLED_APPS.")


router = DefaultRouter()
router.register(r"rooms", ChatRoomViewSet, basename="chat_room")
router.register(r"members", ChatMemberViewSet, basename="chat_member")
router.register(r"messages", ChatMessageViewSet, basename="chat_message")


urlpatterns = [
    path(r"", include(router.urls)),
]
