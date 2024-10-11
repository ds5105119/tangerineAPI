from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    작성자이거나 관리자만 리소스에 접근할 수 있도록 권한 설정.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        if request.user == obj.user:
            return True
        return False
