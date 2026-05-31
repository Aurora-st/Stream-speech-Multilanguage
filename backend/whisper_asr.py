from __future__ import annotations

import math
import re

from faster_whisper import WhisperModel

_model: WhisperModel | None = None
SUPPORTED_WHISPER_LANGUAGES = {"en", "hi", "ja"}


def _normalize_text(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned


def _get_model() -> WhisperModel:
    global _model
    if _model is None:
        _model = WhisperModel("base", compute_type="int8")
    return _model


def transcribe_audio(file_path: str, source_lang: str | None = None) -> dict[str, str | float]:
    """Transcribe audio and return text plus detected language."""
    model = _get_model()
    transcribe_kwargs: dict[str, str] = {}
    if source_lang:
        transcribe_kwargs["language"] = source_lang
    segments, info = model.transcribe(file_path, **transcribe_kwargs)
    parts: list[str] = []
    confidence_values: list[float] = []
    for segment in segments:
        normalized_text = _normalize_text(segment.text)
        if normalized_text:
            parts.append(normalized_text)
        avg_logprob = getattr(segment, "avg_logprob", None)
        if isinstance(avg_logprob, (int, float)):
            confidence_values.append(max(0.0, min(1.0, math.exp(float(avg_logprob)))))
    detected = (source_lang or info.language or "").strip().lower()
    if detected not in SUPPORTED_WHISPER_LANGUAGES:
        detected = "unknown"
    result: dict[str, str | float] = {
        "text": _normalize_text(" ".join(parts)),
        "detected_language": detected,
    }
    if confidence_values:
        result["confidence"] = round(sum(confidence_values) / len(confidence_values), 4)
    return result
