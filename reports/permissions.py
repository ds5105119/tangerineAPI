from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    관리자 권한인 경우, 신고를 처리할 수 있도록 설정
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    로그인 후 사용자가 신고를 작성할 수 있도록 허용.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    """
    신고자는 자신의 신고 목록을 조회할 수 있도록 설정
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
