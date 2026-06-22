from __future__ import annotations

import base64
import hashlib
import mimetypes
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex}"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def safe_extension(filename: str | None, default: str = ".jpg") -> str:
    if not filename:
        return default
    suffix = Path(filename).suffix.lower()
    if re.fullmatch(r"\.[a-z0-9]{1,8}", suffix):
        return suffix
    return default


def guess_mime_type(path: Path) -> str:
    return mimetypes.guess_type(path.name)[0] or "application/octet-stream"


def decode_image_payload(payload: dict) -> tuple[bytes, str]:
    if "image_base64" in payload:
        return base64.b64decode(payload["image_base64"]), payload.get("filename", "image.jpg")

    if "image_path" in payload:
        path = Path(payload["image_path"]).expanduser()
        return path.read_bytes(), path.name

    raise ValueError("Expected image_base64 or image_path.")


def encode_file_base64(path: str | Path) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode("ascii")

