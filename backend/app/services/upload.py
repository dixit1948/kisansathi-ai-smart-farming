"""File upload service — validation, sanitization, storage."""
import os
import io
import uuid
import base64
from typing import Optional, Tuple
from fastapi import UploadFile, HTTPException
import structlog
from app.core.config import settings

logger = structlog.get_logger(__name__)

MAGIC_BYTES = {
    b"\xff\xd8\xff": "image/jpeg",
    b"\x89PNG\r\n\x1a\n": "image/png",
    b"RIFF": "image/webp",  # partial check
}

MAX_SIZE = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024


async def save_upload(upload: UploadFile, user_id: str) -> Tuple[str, Optional[str]]:
    """
    Validate, strip EXIF, save to upload dir outside web root.
    Returns (file_path, base64_data).
    Security: allow-list MIME by magic bytes, random filename, strip GPS.
    """
    content = await upload.read()

    # Size check
    if len(content) > MAX_SIZE:
        raise HTTPException(413, detail={"code": "FILE_TOO_LARGE", "message": f"Max {settings.MAX_UPLOAD_SIZE_MB}MB."})

    # Magic bytes MIME check
    detected_mime = _detect_mime(content)
    if detected_mime not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(415, detail={"code": "INVALID_FILE_TYPE", "message": "Only JPEG, PNG, WebP images allowed."})

    # Strip EXIF/GPS and re-encode using Pillow
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(content))
        img = img.convert("RGB")  # strip EXIF in process
        if img.width > 2048 or img.height > 2048:
            img.thumbnail((2048, 2048))
        output = io.BytesIO()
        img.save(output, format="JPEG", quality=85)
        content = output.getvalue()
    except Exception as e:
        logger.warning("Image re-encode failed — using original", error=str(e))

    # Random filename — no original name used
    filename = f"{uuid.uuid4().hex}.jpg"
    user_dir = os.path.join(settings.UPLOAD_DIR, user_id[:8])
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, filename)

    with open(file_path, "wb") as f:
        f.write(content)

    image_b64 = base64.b64encode(content).decode()
    return file_path, image_b64


async def process_image_upload(upload: UploadFile, user_id: str) -> Optional[str]:
    """Process upload and return base64 only (for chat endpoint)."""
    _, b64 = await save_upload(upload, user_id)
    return b64


def _detect_mime(content: bytes) -> str:
    for magic, mime in MAGIC_BYTES.items():
        if content[:len(magic)] == magic:
            return mime
    # WebP secondary check
    if len(content) > 12 and content[8:12] == b"WEBP":
        return "image/webp"
    return "application/octet-stream"
