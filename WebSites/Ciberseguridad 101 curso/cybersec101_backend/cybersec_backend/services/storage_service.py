"""
File Storage Service — manages physical files on disk.
"""
import uuid
import logging
from pathlib import Path

import aiofiles

from config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

ALLOWED_EXTENSIONS = {
    "application/pdf":       ".pdf",
    "text/plain":            ".txt",
    "text/markdown":         ".md",
    "text/csv":              ".csv",
    "image/jpeg":            ".jpg",
    "image/png":             ".png",
    "image/gif":             ".gif",
    "image/webp":            ".webp",
    "application/msword":    ".doc",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
}


def get_storage_dir() -> Path:
    path = Path(settings.storage_path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_allowed(mime_type: str) -> bool:
    return mime_type in ALLOWED_EXTENSIONS


async def save_file(file_bytes: bytes, mime_type: str, original_name: str) -> str:
    """
    Persist file bytes to disk with a unique name.
    Returns the absolute file path as a string.
    """
    ext = ALLOWED_EXTENSIONS.get(mime_type, Path(original_name).suffix or ".bin")
    unique_name = f"{uuid.uuid4().hex}{ext}"
    dest = get_storage_dir() / unique_name

    async with aiofiles.open(dest, "wb") as f:
        await f.write(file_bytes)

    logger.info("Saved file: %s (%d bytes)", dest, len(file_bytes))
    return str(dest)


def delete_file(file_path: str) -> None:
    p = Path(file_path)
    if p.exists():
        p.unlink()
        logger.info("Deleted file: %s", file_path)


def get_storage_total() -> int:
    """Return total bytes used in the storage directory."""
    return sum(f.stat().st_size for f in get_storage_dir().iterdir() if f.is_file())
