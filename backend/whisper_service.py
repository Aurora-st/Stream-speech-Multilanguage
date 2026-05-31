"""Singleton Whisper model service with async wrappers."""

from __future__ import annotations

import asyncio
from typing import Any

import librosa
import whisper

from config import WHISPER_MODEL

_model: whisper.Whisper | None = None
_model_lock = asyncio.Lock()


def load_whisper_model() -> whisper.Whisper:
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def _transcribe_sync(wav_path: str, source_lang: str | None) -> dict[str, Any]:
    model = load_whisper_model()
    transcribe_kwargs: dict[str, Any] = {
        "fp16": False,
        "temperature": 0,
        "best_of": 1,
        "beam_size": 1,
    }
    if source_lang:
        transcribe_kwargs["language"] = source_lang

    audio_array, _ = librosa.load(wav_path, sr=16000, mono=True)
    result = model.transcribe(audio_array, **transcribe_kwargs)

    segments = result.get("segments") or []
    confidence = None
    if segments:
        logprobs = [seg.get("avg_logprob", -1.0) for seg in segments if "avg_logprob" in seg]
        if logprobs:
            import math

            confidence = round(sum(math.exp(lp) for lp in logprobs) / len(logprobs), 3)

    return {
        "text": (result.get("text") or "").strip(),
        "language": (result.get("language") or source_lang or "unknown").strip().lower(),
        "confidence": confidence,
    }


async def transcribe_audio(wav_path: str, source_lang: str | None = None) -> dict[str, Any]:
    async with _model_lock:
        return await asyncio.to_thread(_transcribe_sync, wav_path, source_lang)
