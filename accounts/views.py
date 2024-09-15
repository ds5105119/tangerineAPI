from accounts.paginators import *
from accounts.permissions import *
from accounts.serializers import *

try:
    from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
    from allauth.socialaccount.providers.oauth2.client import OAuth2Client
    from dj_rest_auth.registration.views import SocialLoginView
    from django.conf import settings
    from django.shortcuts import get_object_or_404
    from rest_framework import generics, permissions, viewsets
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


class UserUpdateView(generics.UpdateAPIView):
    """
    사용자의 정보 업데이트
    PUT
    PATCH
    """

    permission_classes = (UserDataUpdatePermission,)
    queryset = User.objects.all()
    serializer_class = WriteableUserSelfSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    GET /accounts/users/: 사용자 목록을 반환 (페이지네이션 적용)
    GET /accounts/users/?page=2: 두 번째 페이지의 사용자 목록을 반환
    GET /accounts/users/?page_size=10: 페이지 크기를 10으로 설정하여 사용자 목록을 반환
    GET /accounts/users/{handle}/: 특정 handle을 가진 사용자의 상세 정보를 반환
    """

    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination
    lookup_field = "handle"

    def get_object(self):
        queryset = self.get_queryset()
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)
        return obj
