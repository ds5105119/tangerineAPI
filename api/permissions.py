from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthorOrReadOnly(BasePermission):
    """
    when posts author is not request user, only allow SAFE_METHODS
    """
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user


class IsAuthorAndAdmin(BasePermission):
    """
    Only SAFE_METHOD is allowed for general users.
    Other method is provided if user.is_staff = True and Auther is user.
    If user.is_superuser = True, all method is provided.
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user and request.user.is_staff


class UserReplyPermission(BasePermission):
    """
    Create: Authenticate user
    List: Allow all
    Destroy: own self or superuser
    """

    def has_permission(self, request, view):
        if view.action == 'create':
            return request.user.is_authenticated
        elif view.action in ['list', 'Destroy']:
            return True
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action == 'list':
            return True
        elif view.action in ['list', 'Destroy']:
            return obj.user == request.user or request.user.is_superuser
        else:
            return False
