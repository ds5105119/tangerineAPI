from chats.paginators import *
from chats.permissions import *
from chats.serializers import *

try:
    from rest_framework import mixins, status, viewsets
    from rest_framework.exceptions import MethodNotAllowed
    from rest_framework.response import Response
except ImportError:
    raise ImportError("django, django-rest-framework, allauth, dj-rest-accounts needs to be added to INSTALLED_APPS.")


class ChatRoomViewSet(viewsets.ModelViewSet):
    permission_classes = (ChatRoomPermission,)
    pagination_class = ChatRoomPagination
    lookup_url_kwarg = "uuid"
    lookup_field = "uuid"

    def get_queryset(self):
        if self.action in ["retrieve", "list"]:
            current_user = self.request.user
            queryset = (
                ChatRoom.objects.filter(chat_members_as_room__user=current_user)
                .select_related("owner")
                .prefetch_related(
                    Prefetch("chat_members_as_room", queryset=ChatMember.objects.select_related("user__profile"))
                )
            )
            return queryset
        elif self.action in ["update", "partial_update", "destroy"]:
            return ChatRoom.objects.filter(owner=self.request.user)
        raise MethodNotAllowed(self.action)

    def get_serializer_class(self):
        if self.action in ["retrieve", "list"]:
            return ReadOnlyChatRoomSelfSerializer
        elif self.action in ["create", "update", "partial_update"]:
            return WriteableChatRoomSelfSerializer
        raise MethodNotAllowed(self.action)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ChatMemberViewSet(mixins.DestroyModelMixin, viewsets.GenericViewSet):
    permission_classes = (ChatMemberPermission,)
    pagination_class = ChatMemberPagination
    lookup_url_kwarg = "uuid"
    lookup_field = "room_id"

    def get_queryset(self):
        if self.action == "destroy":
            return ChatMember.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ChatMessageViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (ChatMessagePermission,)
    pagination_class = ChatMessagePagination
    lookup_url_kwarg = "uuid"
    lookup_field = "member__room"

    def get_queryset(self):
        if self.action == "retrieve":
            return ChatMessage.objects.all()
        raise MethodNotAllowed(self.action)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ReadOnlyChatMessageSelfSerializer
        raise MethodNotAllowed(self.action)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
