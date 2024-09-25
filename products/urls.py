from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from .views import (
    GetPresignedUrlView,  # AWS S3 버킷의 presigned URL을 얻기 위한 뷰
    LatestProductsAPIView,  # 최신 제품을 조회하는 뷰
    LatestProductsViaHandleAPIView,  # 사용자 핸들로 최신 제품을 조회하는 뷰
    ProductViewSet,  # 제품 관련 CRUD 작업을 수행하는 뷰셋
)

# 기본 라우터 생성 및 제품 뷰셋 등록
router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="product")
urlpatterns = [
    path("", include(router.urls)),  # 등록된 뷰셋의 URL 포함
    path("products/presigned/", GetPresignedUrlView.as_view(), name="presigned"),
    path("products/latest/", LatestProductsAPIView.as_view(), name="latest"),
    re_path(
        r"latest/(?P<handle>[\w.]+)/",
        LatestProductsViaHandleAPIView.as_view(),
        name="user-latest-products",
    ),
]
