from pathlib import Path


class IStorageRepository:
    async def save(self, file_data, file_name):
        raise NotImplementedError

    def get_path(self) -> Path:
        raise NotImplementedError

    def get_url(self, file_name: str) -> str:
        raise NotImplementedError
