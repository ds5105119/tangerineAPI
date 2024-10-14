import logging

from botocore.exceptions import ClientError
from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import PostImage, PresignedUrl
from .serializers import PostImageSerializer
from .services import get_presigned_post

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("default")


class PostImageViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = PostImage.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = PostImageSerializer

    @extend_schema(
        summary="프리사인드 URL 발급 및 DB 저장",
        description="""
        이 엔드포인트는 클라이언트가 AWS S3 버킷에 이미지를 업로드할 수 있도록
        프리사인드 URL을 받아 업로드한 이미지를 Post 모델과 연결합니다=
        """,
        request=PostImageSerializer,
        responses={
            201: OpenApiResponse(response=PostImageSerializer, description="프리사인드 URL 발급 및 DB 저장 성공"),
            400: OpenApiResponse(description="요청이 잘못되었거나 필수 데이터가 누락되었습니다."),
            401: OpenApiResponse(description="인증되지 않은 사용자입니다."),
        },
        tags=["Image Upload"],
    )
    def create(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)


class GetPrivatePresignedUrlView(APIView):
    """
    POST /posts/presigned/: get AWS S3 Bucket presigned post url
    """

    permission_classes = (IsAuthenticated,)
    throttle_scope = "GetPresignedUrlView"
    serializer_class = None

    def get(self, request, *args, **kwargs):
        try:
            presigned_url_data = get_presigned_post(public=True)

            data_to_store = {
                "url": presigned_url_data["url"],
                "is_public": False,
            }
            PresignedUrl.objects.create(**data_to_store)
            return Response(presigned_url_data)
        except ClientError:
            return Response(
                {"error": "문제가 발생했습니다. 나중에 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class GetPublicPresignedUrlView(APIView):
    """
    POST /posts/presigned/: get AWS S3 Bucket presigned post url
    """

    permission_classes = (IsAuthenticated,)
    throttle_scope = "GetPresignedUrlView"
    serializer_class = None

    def get(self, request, *args, **kwargs):
        try:
            presigned_url_data = get_presigned_post(public=True)
            logger.debug(presigned_url_data)

            data_to_store = {
                "url": presigned_url_data["url"],
                "is_public": True,
            }
            PresignedUrl.objects.create(**data_to_store)
            return Response(presigned_url_data)
        except ClientError:
            return Response(
                {"error": "문제가 발생했습니다. 나중에 다시 시도해주세요."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
