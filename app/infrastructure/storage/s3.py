import logging
from asyncio import to_thread
from pathlib import Path
from urllib.parse import urljoin

import boto3

from app.infrastructure.conf import settings
from app.infrastructure.storage.base import IStorageRepository


logger = logging.getLogger(__name__)


class S3StorageRepository(IStorageRepository):
    path = ""

    def __init__(self, path=None):
        self.s3 = boto3.client(
            "s3",
            region_name=settings.AWS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_ACCESS_KEY_SECRET,
            endpoint_url=(settings.AWS_ENDPOINT_URL if settings.AWS_ENDPOINT_URL else None),
        )

        self.bucket_name = settings.AWS_S3_BUCKET_NAME
        self.bucket_url = (
            settings.AWS_S3_BUCKET_URL if settings.AWS_S3_BUCKET_URL else f"https://{self.bucket_name}.s3.amazonaws.com"
        )
        self.path = path or self.path

    async def save(self, file_data, file_name: str):
        logger.info(f"Uploading file {file_name} to {self.bucket_name}")

        await to_thread(
            self.s3.put_object,
            Bucket=self.bucket_name,
            Key=str(file_name),
            Body=file_data,
            ContentType="image/jpeg",
        )
        return urljoin(self.bucket_url, file_name)

    def get_path(self) -> Path:
        return Path(self.path)

    def get_url(self, file_name: str) -> str:
        return urljoin(f"{self.bucket_url}/", file_name)
