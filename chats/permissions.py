from chats.models import *

try:
    from rest_framework.permissions import BasePermission
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class ChatRoomPermission(BasePermission):
    """
    retrieve: 채팅방 상세 보기: 로그인 한 유저만 가능
    list: 자신의 채팅방 리스트: 로그인 한 유저만 가능
    partial_update, update, destroy: 로그인 한 사용자이면서, owner인 경우에만 가능
    """

    def has_permission(self, request, view):
        if view.action in ["retrieve", "list", "create", "partial_update", "update", "destroy"]:
            return request.user.is_authenticated or request.user.is_staff
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ["retrieve", "list", "create"]:
            return True
        if view.action in ["partial_update", "update", "destroy"]:
            return obj.owner == request.user or request.user.is_staff
        return False


class ChatMemberPermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == "destroy":
            return request.user and request.user.is_authenticated or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if view.action == "destroy":
            return True


class ChatMessagePermission(BasePermission):
    def has_permission(self, request, view):
        if view.action == "retrieve":
            return request.user and request.user.is_authenticated or request.user.is_staff

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True
