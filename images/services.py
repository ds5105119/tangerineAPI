from uuid import uuid4

import boto3
import cv2
from botocore.exceptions import ClientError
from django.conf import settings


def resize_image(image, max_resolution):
    height, width = image.shape[:2]
    if height > max_resolution or width > max_resolution:
        scaling_factor = min(max_resolution / height, max_resolution / width)
        new_size = (int(width * scaling_factor), int(height * scaling_factor))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)
    return image


def compress_image(image, initial_quality=95):
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), initial_quality]
    is_success, buffer = cv2.imencode(".jpg", image, encode_param)
    return is_success, buffer.tobytes()


def get_presigned_post(public=False):
    """
    ! Security Warning: DO NOT USE HARDCODED DATA AND DO NOT CHANGE THE CODE
    GET Expires in 2 min AWS S3 bucket presigned url
    :return: presigned post url
    """
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )

    # Returns False if filename does not exist in the AWS S3 bucket.
    def check_object_exists(name):
        try:
            s3_client.head_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=name)
            return True
        except ClientError as error:
            if error.response["Error"]["Code"] == "404":
                return False
            return True

    filename = str(uuid4())
    while check_object_exists(filename):
        filename = str(uuid4())

    try:
        presigned_post = s3_client.generate_presigned_post(
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=filename,
            Fields={"Content-Type": "image/jpeg", "acl": "public-read" if public else "private"},
            Conditions=[
                {"Content-Type": "image/jpeg"},
                ["content-length-range", 1, 1024 * 200],
                {"acl": "public-read" if public else "private"},
            ],
            ExpiresIn=60,
        )

        presigned_post["filename"] = filename

        return presigned_post
    except ClientError as e:
        raise e
