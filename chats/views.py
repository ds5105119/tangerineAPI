from chats.serializers import *

try:
    from rest_framework import viewsets
    from rest_framework.exceptions import MethodNotAllowed
except ImportError:
    raise ImportError("django, django-rest-framework, allauth, dj-rest-accounts needs to be added to INSTALLED_APPS.")


class ChatRoomViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return WriteableChatRoomSelfSerializer

        raise MethodNotAllowed(self.action)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        serializer.save()
