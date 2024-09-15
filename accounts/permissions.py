try:
    from rest_framework.permissions import BasePermission
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class UserDataUpdatePermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in ["PUT", "PATCH"]:
            return True

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.is_staff:
            return True
        elif obj.user == request.user:
            return True
        return False
