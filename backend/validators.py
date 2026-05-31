"""Request validation helpers."""

from __future__ import annotations

from fastapi import HTTPException, UploadFile

from config import ALLOWED_AUDIO_CONTENT_TYPES, MAX_UPLOAD_BYTES


def validate_upload(upload: UploadFile, audio_bytes: bytes) -> None:
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio file is empty")

    if len(audio_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds maximum size of {MAX_UPLOAD_BYTES // (1024 * 1024)} MB",
        )

    content_type = (upload.content_type or "application/octet-stream").split(";")[0].strip()
    if content_type not in ALLOWED_AUDIO_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported audio content type: {content_type}",
        )
