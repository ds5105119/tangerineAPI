try:
    from rest_framework.permissions import BasePermission
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class UserPermission(BasePermission):
    """
    retrieve: 유저 프로필 개별 조회는 모든 사람이 가능
    list: 유저 프로필 여러개 조회는 로그인 한 사람만 가능
    partial_update, update, destroy: 유저 프로필 부분 업데이트, 업데이트 및 삭제는 해당 유저 또는 관리자만 가능
    """

    def has_permission(self, request, view):
        if view.action == "retrieve":
            return True
        if view.action in ["list", "partial_update", "update", "destroy"]:
            return request.user and request.user.is_authenticated
        return False

    def has_object_permission(self, request, view, obj):
        if view.action in ["retrieve", "list"]:
            return True
        if view.action in ["partial_update", "update", "destroy"]:
            return obj == request.user or request.user.is_staff
        return False
