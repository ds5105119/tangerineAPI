from accounts.views import *

try:
    from dj_rest_auth.app_settings import api_settings
    from dj_rest_auth.views import (
        LoginView,
        LogoutView,
        PasswordChangeView,
        PasswordResetConfirmView,
        PasswordResetView,
    )
    from django.urls import include, path
    from rest_framework.routers import DefaultRouter
except ImportError:
    raise ImportError("django, django rest framework, simplejwt needs to be added to INSTALLED_APPS.")


router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

# 사용자 정의 urlpatterns
urlpatterns = [
    path("google/login/", GoogleLogin.as_view(), name="google_login"),
    path("users/", include(router.urls), name="user"),
]

# dj-rest-auth urls(일부만 사용)
urlpatterns += [
    path("password/reset/", PasswordResetView.as_view(), name="rest_password_reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="rest_password_reset_confirm"),
    path("password/change/", PasswordChangeView.as_view(), name="rest_password_change"),
    path("login/", LoginView.as_view(), name="rest_login"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("registration/", include("dj_rest_auth.registration.urls")),
]

# JWT 사용 시 추가
if api_settings.USE_JWT:
    from dj_rest_auth.jwt_auth import get_refresh_view
    from rest_framework_simplejwt.views import TokenVerifyView

    urlpatterns += [
        path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
        path("token/refresh/", get_refresh_view().as_view(), name="token_refresh"),
    ]
