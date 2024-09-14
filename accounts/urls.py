from accounts.views import GoogleLogin, UserHandleCreateView, UserViewSet

try:
    from dj_rest_auth.views import LogoutView
    from django.urls import include, path
    from rest_framework.routers import DefaultRouter
    from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
except ImportError:
    raise ImportError("django, django rest framework, simplejwt needs to be added to INSTALLED_APPS.")


router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("google/login/", GoogleLogin.as_view(), name="google_login"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", LogoutView.as_view(), name="rest_logout"),
    path("handle/", UserHandleCreateView.as_view(), name="handle"),
    path("", include(router.urls), name="user"),
]
