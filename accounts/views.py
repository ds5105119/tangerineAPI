from accounts.paginators import *
from accounts.permissions import *
from accounts.serializers import *

try:
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.client import OAuth2Client
    from dj_rest_auth.registration.views import SocialLoginView
    from django.conf import settings
    from drf_spectacular.utils import OpenApiParameter, OpenApiResponse, extend_schema
    from rest_framework import mixins, viewsets
    from rest_framework.exceptions import MethodNotAllowed
except ImportError:
    raise ImportError("django, django-rest-framework, allauth, dj-rest-accounts needs to be added to INSTALLED_APPS.")


class GoogleLogin(SocialLoginView):
    """
    allauth, dj-rest-auth social login view
    """

    adapter_class = GoogleOAuth2Adapter
    callback_url = settings.GOOGLE_REDIRECT_URI
    client_class = OAuth2Client
    serializer_class = CustomSocialLoginSerializer


class UserViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    permission_classes = (UserPermission,)
    pagination_class = UserPagination
    lookup_field = "handle"
    lookup_value_regex = r"[\w.]+"

    def get_queryset(self):
        fields = self.get_serializer_class().Meta.fields
        foreign_fields = ["profile"]
        non_foreign_fields = [field for field in fields if field not in foreign_fields]

        if self.action in ["retrieve", "list", "partial_update", "update", "destroy"]:
            return User.objects.select_related("profile").only(*non_foreign_fields)
        raise MethodNotAllowed(self.action)

    def get_serializer_class(self):
        if self.action == "retrieve":
            if self.get_object().user == self.request.user:
                return ReadOnlyUserSelfSerializer
            return ReadOnlyUserExternalSerializer
        elif self.action == "list":
            return ReadOnlyUserExternalSerializer
        elif self.action in ["partial_update", "update"]:
            return WriteableUserSelfSerializer
        raise MethodNotAllowed(self.action)

    @extend_schema(
        summary="유저의 정보를 반환합니다.",
        description="handle을 통해 유저의 정보를 반환합니다. 자신인 경우 email 필드가 추가됩니다. 모든 사용자가 사용할 수 있습니다.",
        responses={200: ReadOnlyUserExternalSerializer, 403: OpenApiParameter("Unauthorized access")},
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="최신 유저의 리스트를 반환합니다",
        description="최신 유저의 리스트를 반환합니다. 오직 인증된 사용자만 사용할 수 있습니다. 이후 업데이트에서는 추천 유저 리스트가 될 것입니다.",
        responses={
            200: ReadOnlyUserExternalSerializer(many=True),
            403: OpenApiParameter("Unauthorized access"),
        },
        parameters=[
            OpenApiParameter("page", int, description="Page number for pagination", required=False),
            OpenApiParameter("page_size", int, description="Number of results per page", required=False),
        ],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="유저의 정보를 부분만 업데이트합니다",
        description="handle을 통해 유저의 정보를 부분만 업데이트합니다. 오직 유저 자신 또는 staff만 사용할 수 있습니다.",
        request=WriteableUserSelfSerializer,
        responses={
            200: WriteableUserSelfSerializer,
            403: OpenApiParameter("Unauthorized access"),
        },
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        summary="유저의 정보를 업데이트합니다",
        description="handle을 통해 유저의 정보를 업데이트합니다. 오직 유저 자신 또는 staff만 사용할 수 있습니다.",
        request=WriteableUserSelfSerializer,
        responses={
            200: WriteableUserSelfSerializer,
            403: OpenApiParameter("Unauthorized access"),
        },
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="유저를 삭제합니다",
        description="handle을 통해 유저의 정보를 삭제합니다. 오직 유저 자신 또는 staff만 사용할 수 있습니다.",
        responses={
            204: OpenApiResponse(description="No content, profile deleted successfully"),
            403: OpenApiResponse(description="Unauthorized access"),
        },
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
