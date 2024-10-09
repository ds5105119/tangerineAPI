from chats.paginators import *
from chats.permissions import *
from chats.serializers import *

try:
    from django.db.models import Prefetch
    from drf_spectacular.utils import OpenApiResponse, extend_schema
    from rest_framework import mixins, status, viewsets
    from rest_framework.decorators import action
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
                    Prefetch("chat_members_as_room", queryset=ChatMember.objects.select_related("user__profile")),
                    Prefetch("chat_members_as_room__chat_messages_as_member", queryset=ChatMessage.objects.all()),
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


class ChatMessageViewSet(viewsets.GenericViewSet):
    permission_classes = (ChatMessagePermission,)
    pagination_class = ChatMessagePagination
    lookup_url_kwarg = "uuid"
    lookup_field = "member__room"
    queryset = ChatMessage.objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == "messages":
            return queryset
        raise MethodNotAllowed(self.action)

    def get_serializer_class(self):
        if self.action == "messages":
            return ReadOnlyChatMessageSelfSerializer
        raise MethodNotAllowed(self.action)

    def get_paginated_response_data(self, queryset):
        """
        Helper method to handle pagination and serialization
        """
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        description="uuid를 사용해 채팅방의 메시지를 반환합니다.",
        responses={
            200: ReadOnlyChatMessageSelfSerializer(many=True),
            400: OpenApiResponse(description="Bad Request"),
        },
    )
    @action(detail=True, methods=["get"], url_path="", url_name="")
    def messages(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        assert lookup_url_kwarg in self.kwargs, (
            "Expected view %s to be called with a URL keyword argument "
            f'named "{(self.__class__.__name__, lookup_url_kwarg)}". Fix your URL conf, or set the `.lookup_field` '
            "attribute on the view correctly."
        )

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        queryset = queryset.filter(**filter_kwargs)

        return self.get_paginated_response_data(queryset)
