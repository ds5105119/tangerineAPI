from rest_framework.permissions import BasePermission


class FollowPermission(BasePermission):
    """
    create: 로그인 한 사용자 또는 스태프만 가능
    follows, followers: 모두가 사용 가능
    unfollow, unfollower: 유저 자신 또는 스태프만 사용 가능
    """

    def has_permission(self, request, view):
        if view.action in ["follows", "followers"]:
            return True
        elif view.action in ["create", "unfollow", "unfollower"]:
            return request.user.is_authenticated or request.user.is_staff
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if view.action in ["follows", "followers", "create"]:
            return True
        elif view.action == "unfollow":
            return obj.follower == request.user or request.user.is_staff
        elif view.action == "unfollow":
            return obj.user == request.user or request.user.is_staff
        else:
            return False
