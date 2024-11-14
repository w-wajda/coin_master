from pathlib import Path

from app.infrastructure.storage.base import IStorageRepository


class FakeS3StorageRepository(IStorageRepository):
    path = ""

    def __init__(self, path=None):
        self.path = path or self.path
        self.storage = {}

    async def save(self, file_data, file_name):
        self.storage[file_name] = file_data
        return f"https://foo_bucket.fake.s3.com{file_name}"

    def get_path(self) -> Path:
        return Path(self.path)

    def get_url(self, file_name: str) -> str:
        return f"https://foo_bucket.fake.s3.com{file_name}"
