"""Application configuration from environment variables."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent

STATIC_DIR = BASE_DIR / "static"
STATIC_AUDIO_DIR = STATIC_DIR / "audio"
TEMP_AUDIO_DIR = BASE_DIR / "temp_audio"
DATA_DIR = BASE_DIR / "data"

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
API_HOST = os.getenv("API_HOST", "127.0.0.1")
API_PORT = int(os.getenv("API_PORT", "8000"))
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", f"http://{API_HOST}:{API_PORT}")

CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", "3600"))
CACHE_MAX_ENTRIES = int(os.getenv("CACHE_MAX_ENTRIES", "256"))

CORS_ORIGINS = [
    origin.strip()
    for origin in os.getenv("CORS_ORIGINS", "*").split(",")
    if origin.strip()
]

DATABASE_PATH = Path(os.getenv("DATABASE_PATH", str(DATA_DIR / "analytics.db")))

MAX_UPLOAD_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", str(10 * 1024 * 1024)))  # 10 MB
ALLOWED_AUDIO_CONTENT_TYPES = {
    t.strip()
    for t in os.getenv(
        "ALLOWED_AUDIO_CONTENT_TYPES",
        "audio/webm,audio/ogg,audio/wav,audio/mpeg,audio/mp4,application/octet-stream",
    ).split(",")
    if t.strip()
}
