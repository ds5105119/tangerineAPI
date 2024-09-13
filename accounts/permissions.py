try:
    from rest_framework.permissions import BasePermission
except ImportError:
    raise ImportError("django-rest-framework needs to be added to INSTALLED_APPS.")


class HandlePermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        elif view.action == "Retrieve":
            return True
        else:
            return obj == request.user
