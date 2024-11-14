import io
from dataclasses import dataclass

from PIL import Image


@dataclass
class ThumbnailSize:
    width: int
    height: int
    quality: int = 100


class ThumbnailGenerator:
    @staticmethod
    def generate(image_data: bytes, size: ThumbnailSize) -> bytes:
        """Generate a thumbnail from the given image data and size."""
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((size.width, size.height))
        output = io.BytesIO()
        image.save(output, format=image.format)
        return output.getvalue()
