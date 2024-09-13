from accounts.models import User
from follows.models import Follow
from follows.permissions import FollowPermission
from follows.serializers import FollowerSerializer, FollowingSerializer

try:
    from django.db.models import F
    from django.conf import settings
    from django.shortcuts import get_object_or_404
    from rest_framework import status, mixins, generics, viewsets
    from rest_framework.exceptions import ValidationError
    from rest_framework.response import Response
    from rest_framework.permissions import AllowAny
except ImportError:
    raise ImportError(
        "django, django-rest-framework, allauth, dj-rest-accounts needs to be added to INSTALLED_APPS."
    )


class FollowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    유저의 팔로워와 팔로잉에 대한 ViewSet입니다.
    GET: 팔로워와 팔로잉 리스트, request: { handle: User.handle }
    POST: 팔로우, request: { handle: User.handle }
    DELETE: 팔로우 또는 팔로워 삭제, request: { "handle": User.handle, "delete_option": "following" | "follower" }
    """

    permission_classes = (FollowPermission,)

    def get_serializer_class(self):
        if self.action == "create":
            return FollowingSerializer
        elif self.action == "destroy":
            return FollowerSerializer
        return super().get_serializer_class()

    def list(self, request, *args, **kwargs):
        handle = request.GET.get("handle")
        user = get_object_or_404(User, handle=handle)

        following = Follow.objects.filter(follower=user)
        followers = Follow.objects.filter(user=user)

        following_serializer = FollowingSerializer(following, many=True)
        followers_serializer = FollowerSerializer(followers, many=True)

        return Response(
            {
                "following": following_serializer.data,
                "followers": followers_serializer.data,
            }
        )

    def perform_create(self, serializer):
        user = self.request.user
        handle = self.request.data.get("handle")
        user_to_follow = get_object_or_404(User, handle=handle)

        if user == user_to_follow:
            raise ValidationError("You cannot follow yourself.")
        else:
            user.update(follows_count=F("follows_count") + 1)
            user_to_follow.objects.update(followers_count=F("followers_count") + 1)
            user.refresh_from_db()
            user_to_follow.refresh_from_db()

        serializer.save(follower=user, user=user_to_follow)
        return Response(
            {"detail": "Successfully followed."}, status=status.HTTP_204_NO_CONTENT
        )

    def destroy(self, request, *args, **kwargs):
        user = request.user
        handle = request.data.get("handle")
        instance = get_object_or_404(User, handle=handle)
        delete_option = request.data.get("delete")

        if not delete_option or not handle:
            return Response(
                {"detail": "Invalid request. 'delete' and 'handle' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if delete_option == "follower":
            follow_instance = Follow.objects.filter(
                user=user, follower=instance
            ).first()
            if follow_instance:
                follow_instance.delete()
                return Response(
                    {"detail": "Follower removed successfully."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"detail": "This user is not your follower."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        elif delete_option == "following":
            follow_instance = Follow.objects.filter(
                user=instance, follower=user
            ).first()
            if follow_instance:
                follow_instance.delete()
                return Response(
                    {"detail": "Successfully unfollowed."},
                    status=status.HTTP_204_NO_CONTENT,
                )
            return Response(
                {"detail": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"detail": "Invalid delete option."}, status=status.HTTP_400_BAD_REQUEST
        )
