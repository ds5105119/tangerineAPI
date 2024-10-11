import boto3
import cv2
import numpy as np
from botocore.exceptions import ClientError
from django.conf import settings
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response

from posts.models import Post

from .models import PostImage
from .serializers import PostImageSerializer
from .services import get_presigned_post


class PostImageViewSet(viewsets.GenericViewSet):
    queryset = PostImage.objects.all()
    serializer_class = PostImageSerializer
    parser_classes = (MultiPartParser,)

    @extend_schema(
        summary="프리사인드 URL 발급 및 DB 저장",
        description="AWS S3의 presigned URL 호출 결과를 저장하고 반환합니다. 이미지를 S3 버킷에 업로드합니다.",
        request={
            "type": "multipart/form-data",
            "properties": {
                "post": {"type": "string", "description": "포스트 UUID"},
                "file": {
                    "type": "string",
                    "format": "binary",
                    "description": "업로드할 이미지 파일",
                },
            },
        },
        responses={201: PostImageSerializer},
    )
    def create(self, request):
        try:
            user = request.user
            post_uuid = request.data.get("post")
            file = request.FILES.get("file")
            if not post_uuid or not file:
                return Response(
                    {"error": "Post UUID and file are required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            post = get_object_or_404(Post, uuid=post_uuid)
            presigned_url_data = get_presigned_post()

            file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

            if image is None:
                return Response(
                    {"error": "유효하지 않은 이미지 파일입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            height, width = image.shape[:2]
            max_resolution = 2000

            if height > max_resolution or width > max_resolution:
                scaling_factor = min(max_resolution / float(height), max_resolution / float(width))
                new_size = (int(width * scaling_factor), int(height * scaling_factor))
                image = cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

            is_success, buffer = cv2.imencode(".jpg", image)
            image_bytes = buffer.tobytes()

            if len(image_bytes) > 150 * 1024:
                quality = int((150 * 1024) / len(image_bytes) * 100)
                is_success, buffer = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
                image_bytes = buffer.tobytes()

            data_to_store = {
                "user": user,
                "post": post,
                "url": presigned_url_data["url"],
                "key": presigned_url_data["fields"]["key"],
                "content_type": presigned_url_data["fields"]["Content-Type"],
                "policy": presigned_url_data["fields"]["policy"],
                "signature": presigned_url_data["fields"]["signature"],
            }

            post_image = PostImage.objects.create(**data_to_store)

            s3_client = boto3.client(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            )

            response = s3_client.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=presigned_url_data["fields"]["key"],
                Body=image_bytes,
                ContentType=presigned_url_data["fields"]["Content-Type"],
            )

            if response["ResponseMetadata"]["HTTPStatusCode"] != 200:
                raise ValidationError("이미지 업로드에 실패했습니다.")

            serializer = self.get_serializer(post_image)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ClientError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
