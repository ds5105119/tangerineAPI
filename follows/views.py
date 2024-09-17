from follows.models import *
from follows.permissions import *
from follows.serializers import *

try:
    from django.contrib.auth import get_user_model
    from django.db import IntegrityError, transaction
    from django.db.models import F
    from drf_spectacular.utils import OpenApiExample, OpenApiResponse, extend_schema
    from rest_framework import mixins, status, viewsets
    from rest_framework.decorators import action
    from rest_framework.exceptions import MethodNotAllowed, NotFound, ValidationError
    from rest_framework.response import Response
except ImportError:
    raise ImportError("django, django-rest-framework, allauth, dj-rest-accounts needs to be added to INSTALLED_APPS.")


User = get_user_model()


class FollowingViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = (FollowPermission,)
    lookup_field = "handle"
    lookup_value_regex = r"[\w.]+"

    def get_serializer_class(self):
        if self.action == "create":
            return WritableFollowSelfSerializer
        elif self.action == "follows":
            return ReadOnlyFollowerExternalSerializer
        elif self.action == "followers":
            return ReadOnlyFollowingExternalSerializer
        raise MethodNotAllowed(self.action)

    def get_paginated_response_data(self, queryset):
        """
        Helper method to handle pagination and serialization
        """
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def handle_unfollow(self, queryset, error_message):
        if queryset.exists():
            follow_instance = queryset.first()
            follow_instance.delete()
            return Response({"detail": "Follower removed successfully."}, status=status.HTTP_204_NO_CONTENT)
        return Response({"detail": error_message}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        description="현재 로그인한 유저가 특정 handle를 소유한 유저를 팔로우하게 합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {"handle": {"type": "string", "description": "Handle of the user to follow"}},
            }
        },
        responses={
            201: None,
            400: OpenApiExample(
                "Invalid Input", summary="Bad Request Example", value={"detail": "You cannot follow yourself."}
            ),
            409: OpenApiExample(
                "Conflict", summary="Conflict Example", value={"detail": "You are already following this user."}
            ),
        },
    )
    def perform_create(self, serializer):
        user = self.request.user
        user_to_follow = serializer.validated_data.get("user")

        if user.handle == user_to_follow.handle:
            raise ValidationError("You cannot follow yourself.")
        else:
            try:
                with transaction.atomic():
                    Follow.objects.create(follower=user, user=user_to_follow).save()
                    user.follows_count = F("follows_count") + 1
                    user.save(update_fields=["follows_count"])
                    user_to_follow.followers_count = F("followers_count") + 1
                    user_to_follow.save(update_fields=["followers_count"])
            except IntegrityError:
                raise ValidationError("You are already following this user. or DB Error")

    @extend_schema(
        description="handle를 사용하여 유저의 팔로우 목록을 반환합니다.",
        responses={200: ReadOnlyFollowerExternalSerializer(many=True), 400: OpenApiResponse(description="Bad Request")},
    )
    @action(detail=True, methods=["get"])
    def follows(self, request, *args, **kwargs):
        handle = self.kwargs.get(self.lookup_field)
        if not User.objects.filter(handle=handle).exists():
            raise NotFound("The requested object was not found.")
        follows_queryset = Follow.objects.filter(follower__handle=handle).select_related("user")
        return self.get_paginated_response_data(follows_queryset)

    @extend_schema(
        description="handle를 사용하여 유저의 팔로워 목록을 반환합니다.",
        responses={
            200: ReadOnlyFollowingExternalSerializer(many=True),
            400: OpenApiResponse(description="Bad Request"),
        },
    )
    @action(detail=True, methods=["get"])
    def followers(self, request, *args, **kwargs):
        handle = self.kwargs.get(self.lookup_field)
        if not User.objects.filter(handle=handle).exists():
            raise NotFound("The requested object was not found.")
        followers_queryset = Follow.objects.filter(user__handle=handle).select_related("follower")
        return self.get_paginated_response_data(followers_queryset)

    @extend_schema(
        description="handle을 통해 유저의 팔로우를 삭제합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {"handle": {"type": "string", "description": "Handle of the user to unfollow"}},
            }
        },
        responses={204: None, 400: OpenApiResponse(description="Bad Request")},
    )
    @action(detail=True, methods=["delete"])
    def unfollow(self, request, *args, **kwargs):
        handle = self.kwargs.get(self.lookup_field)
        user = self.request.user
        follows_queryset = Follow.objects.filter(user__handle=handle, follower=user)
        return self.handle_unfollow(follows_queryset, "You are not following this user.")

    @extend_schema(
        description="handle을 통해 유저의 팔로워를 삭제합니다.",
        request={
            "application/json": {
                "type": "object",
                "properties": {"handle": {"type": "string", "description": "Handle of the follower to remove"}},
            }
        },
        responses={204: None, 400: OpenApiResponse(description="Bad Request")},
    )
    @action(detail=True, methods=["delete"])
    def unfollower(self, request, *args, **kwargs):
        handle = self.kwargs.get(self.lookup_field)
        user = self.request.user
        followers_queryset = Follow.objects.filter(user=user, follower__handle=handle)
        return self.handle_unfollow(followers_queryset, "This user is not your follower.")
