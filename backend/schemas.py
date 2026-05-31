from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class Language(str, Enum):
    EN = "en"
    HI = "hi"
    JA = "ja"
    ES = "es"
    TA = "ta"


SUPPORTED_PAIRS = {
    ("ja", "en"),
    ("en", "hi"),
    ("hi", "en"),
    ("en", "es"),
    ("es", "en"),
    ("ta", "hi"),
    ("hi", "ta"),
}


class Latency(BaseModel):
    asr: float
    translation: float
    tts: float
    total: float


class TranslationResponse(BaseModel):
    source_text: str
    translated_text: str
    audio_url: str
    detected_language: str
    confidence: float | None = None
    translation_confidence: float | None = None
    sentiment: str = "neutral"
    sentiment_score: float = 0.5
    keywords: list[str] = Field(default_factory=list)
    summary: str = ""
    audio_duration_ms: float | None = None
    cached: bool = False
    latency: Latency


class AnalyticsStats(BaseModel):
    total_translations: int
    average_latency_ms: float
    average_audio_duration_ms: float
    average_latency_breakdown: Latency
    cached_responses: int
    success_rate_percent: float
    total_requests: int
    failed_requests: int
    most_used_language: str | None
    languages_used: list[dict[str, int | str]]
    detected_languages: list[dict[str, int | str]]
    sentiment_distribution: list[dict[str, int | str]]
    cache_stats: dict[str, int | float]


class HealthResponse(BaseModel):
    status: str
    whisper_model: str
    cache_entries: int
    database: str = "connected"
