import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from uuid import uuid4


def get_presigned_post():
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
            Fields={"Content-Type": "image/jpeg"},
            Conditions=[{"Content-Type": "image/jpeg"}, ["content-length-range", 1, 1024 * 200]],
            ExpiresIn=60,
        )

        presigned_post["filename"] = filename

        return presigned_post
    except ClientError as e:
        raise e
