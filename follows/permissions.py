from rest_framework.permissions import BasePermission


class FollowPermission(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
        elif view.action == 'list':
            return True
        elif view.action in ['create', 'Destroy']:
            return request.user.is_authenticated
        else:
            return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        elif view.action == 'create':
            # 자기 자신을 팔로우할 수 없음
            return obj.user != request.user
        elif view.action == 'destroy':
            delete_option = request.data.get('delete')
            # 자신의 팔로워만 제거 가능
            if delete_option == 'follower':
                return obj.user == request.user
            # 자신이 팔로우한 사람만 언팔로우 가능
            elif delete_option == 'following':
                return obj.follower == request.user
        return False
