from django.conf import settings
from rest_framework.permissions import BasePermission


class UserProductAllow(BasePermission):
    """
    Create: Authenticated user
    Retrieve: Allow all
    Update, Partial update, Destroy: own self or staff
    """

    def has_permission(self, request, view):
        if view.action == "create":
            return request.user.is_authenticated
        elif view.action in ["retrieve", "update", "partial_update", "destroy"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True
        elif view.action in ["update", "partial_update", "destroy"]:
            return obj.user == request.user or request.user.is_staff
        return False


class UserProductProhibit(BasePermission):
    """
    List, Create: Admin only
    Retrieve: Allow all
    Update, Partial update, Destroy: own self or superuser
    """

    def has_permission(self, request, view):
        if view.action in ["list", "create"]:
            return request.user.is_authenticated and request.user.is_staff
        elif view.action in ["retrieve", "update", "partial_update", "destroy"]:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if view.action == "retrieve":
            return True
        elif view.action in ["update", "partial_update", "destroy"]:
            return obj.user == request.user or request.user.is_staff
        else:
            return False


UserProductWritable = getattr(settings, "tangerineAPI", {}).get("UserProductWritable", True)
ProductPermissions = UserProductAllow if UserProductWritable else UserProductProhibit
