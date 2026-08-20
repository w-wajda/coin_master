from pathlib import Path

from app.infrastructure.storage.base import IStorageRepository


class FakeS3StorageRepository(IStorageRepository):
    """In-memory storage do testów — bez sieci, bez Dockera, bez MinIO."""

    path = ""

    def __init__(self, path=None):
        self.path = path or self.path
        self.files: dict[str, bytes] = {}

    async def save(self, file_data, file_name: str):
        self.files[str(file_name)] = file_data
        return self.get_url(file_name)

    def get_path(self) -> Path:
        return Path(self.path)

    def get_url(self, file_name: str) -> str:
        return f"http://fake-s3.local/{file_name}"
