from __future__ import annotations

import os
from fastapi import UploadFile

from ...config import settings


def uploads_base_dir() -> str:
    # storage/uploads/
    return os.path.join(settings.storage_dir, settings.upload_dir)


def ensure_upload_dirs() -> None:
    os.makedirs(uploads_base_dir(), exist_ok=True)


def save_upload(file: UploadFile) -> str:
    """Save file to storage/uploads/ and return basename."""
    ensure_upload_dirs()

    original_name = file.filename or ""
    basename = os.path.basename(original_name)
    if not basename:
        raise ValueError("Invalid filename")

    dst_path = os.path.join(uploads_base_dir(), basename)

    # Stream to disk
    with open(dst_path, "wb") as f:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            f.write(chunk)

    return basename


def resolve_upload_path(basename: str) -> str:
    if not basename:
        raise ValueError("basename is required")
    safe_name = os.path.basename(basename)
    path = os.path.join(uploads_base_dir(), safe_name)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Uploaded file not found: {safe_name}")
    return path

