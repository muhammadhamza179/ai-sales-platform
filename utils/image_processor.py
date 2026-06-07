import base64
import io
from PIL import Image


def process_image(file_bytes: bytes, max_size: int = 1568) -> str:
    image = Image.open(io.BytesIO(file_bytes))
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    width, height = image.size
    if width > max_size or height > max_size:
        ratio = min(max_size / width, max_size / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        image = image.resize((new_width, new_height), Image.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")