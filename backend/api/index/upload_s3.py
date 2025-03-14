import os
import boto3
import logging
from botocore.exceptions import ClientError
from fastapi import UploadFile

class UploadS3:
    def __init__(self):
        self.bucket_name = os.getenv("AWS_BUCKET")
        self.s3_client = boto3.client("s3")

    async def upload_file(self, file: UploadFile, object_name: str) -> bool:
        try:
            file_content = await file.read()
            self.s3_client.put_object(Body=file_content, Bucket=self.bucket_name, Key=object_name)
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def get_s3_uri(self, object_name: str) -> str:
        return f"s3://{self.bucket_name}/{object_name}"