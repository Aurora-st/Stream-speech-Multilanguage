"""Production FastAPI application for StreamSpeech."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from time import perf_counter
from uuid import uuid4

import cache_guard  # noqa: F401 — must run before model imports
import librosa
from analytics import analytics_store
from cache import translation_cache
from config import (
    CORS_ORIGINS,
    PUBLIC_BASE_URL,
    STATIC_AUDIO_DIR,
    STATIC_DIR,
    TEMP_AUDIO_DIR,
    WHISPER_MODEL,
)
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from googletrans import Translator
from gtts import gTTS
from middleware import register_exception_handlers
from nlp import (
    analyze_sentiment,
    estimate_translation_confidence,
    extract_keywords,
    generate_summary,
)
from schemas import SUPPORTED_PAIRS, AnalyticsStats, HealthResponse, TranslationResponse
from validators import validate_upload
from whisper_service import load_whisper_model, transcribe_audio

try:
    from .audio_convert import convert_webm_to_wav
except ImportError:
    from audio_convert import convert_webm_to_wav

_translator: Translator | None = None


def _get_translator() -> Translator:
    global _translator
    if _translator is None:
        _translator = Translator()
    return _translator


async def _translate_text(text: str, source_lang: str, target_lang: str) -> str:
    cache_key = translation_cache.make_text_key(text, source_lang, target_lang)
    cached = translation_cache.get(cache_key)
    if cached and "translated_text" in cached:
        return cached["translated_text"]

    def _sync_translate() -> str:
        return _get_translator().translate(text, src=source_lang, dest=target_lang).text

    translated = await asyncio.to_thread(_sync_translate)
    translation_cache.set(cache_key, {"translated_text": translated})
    return translated


async def _generate_tts(text: str, target_lang: str, output_path: str) -> None:
    def _sync_tts() -> None:
        gTTS(text=text, lang=target_lang).save(output_path)

    await asyncio.to_thread(_sync_tts)


def _audio_duration_ms(wav_path: str) -> float:
    duration = librosa.get_duration(path=wav_path)
    return round(duration * 1000, 2)


@asynccontextmanager
async def lifespan(app: FastAPI):
    TEMP_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    STATIC_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(load_whisper_model)
    yield


app = FastAPI(title="StreamSpeech API", version="2.1.0", lifespan=lifespan)
register_exception_handlers(app)

allow_origins = CORS_ORIGINS if CORS_ORIGINS != ["*"] else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root() -> dict[str, str]:
    return {"status": "Backend running", "version": "2.1.0"}


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    cache_stats = translation_cache.stats()
    return HealthResponse(
        status="ok",
        whisper_model=WHISPER_MODEL,
        cache_entries=int(cache_stats["entries"]),
        database="connected",
    )


@app.get("/analytics/stats", response_model=AnalyticsStats)
async def analytics_stats() -> AnalyticsStats:
    stats = analytics_store.get_stats()
    cache_stats = translation_cache.stats()
    breakdown = stats["average_latency_breakdown"]
    return AnalyticsStats(
        total_translations=stats["total_translations"],
        average_latency_ms=stats["average_latency_ms"],
        average_audio_duration_ms=stats["average_audio_duration_ms"],
        average_latency_breakdown={
            "asr": breakdown["asr"],
            "translation": breakdown["translation"],
            "tts": breakdown["tts"],
            "total": breakdown["total"],
        },
        cached_responses=stats["cached_responses"],
        success_rate_percent=stats["success_rate_percent"],
        total_requests=stats["total_requests"],
        failed_requests=stats["failed_requests"],
        most_used_language=stats["most_used_language"],
        languages_used=stats["languages_used"],
        detected_languages=stats["detected_languages"],
        sentiment_distribution=stats["sentiment_distribution"],
        cache_stats=cache_stats,
    )


@app.get("/analytics/history")
async def analytics_history(limit: int = 20) -> dict[str, list]:
    return {"history": analytics_store.get_history(limit=min(limit, 100))}


@app.post("/translate-speech", response_model=TranslationResponse)
async def translate_speech(
    file: UploadFile | None = File(default=None),
    audio: UploadFile | None = File(default=None),
    source_lang: str | None = Form(default=None),
    target_lang: str = Form(...),
) -> TranslationResponse:
    total_started = perf_counter()
    upload = file or audio
    if upload is None:
        raise HTTPException(status_code=400, detail="No audio file provided")

    if source_lang and source_lang == target_lang:
        raise HTTPException(status_code=400, detail="Source and target languages must be different")
    if source_lang and (source_lang, target_lang) not in SUPPORTED_PAIRS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported translation pair: {source_lang}->{target_lang}",
        )

    audio_bytes = await upload.read()
    validate_upload(upload, audio_bytes)

    cache_key = translation_cache.make_audio_key(audio_bytes, source_lang, target_lang)
    cached_result = translation_cache.get(cache_key)
    if cached_result:
        cached_result["cached"] = True
        cached_result["latency"]["total"] = round((perf_counter() - total_started) * 1000, 2)
        analytics_store.record_request(
            endpoint="/translate-speech",
            status="success",
            target_lang=target_lang,
            latency_ms=cached_result["latency"]["total"],
        )
        return TranslationResponse(**cached_result)

    request_id = uuid4().hex
    input_webm = TEMP_AUDIO_DIR / f"input_{request_id}.webm"
    input_wav = TEMP_AUDIO_DIR / f"input_{request_id}.wav"
    output_mp3 = STATIC_AUDIO_DIR / f"{request_id}.mp3"

    try:
        input_webm.write_bytes(audio_bytes)
        await asyncio.to_thread(convert_webm_to_wav, str(input_webm), str(input_wav))
        audio_duration_ms = await asyncio.to_thread(_audio_duration_ms, str(input_wav))

        asr_started = perf_counter()
        asr_result = await transcribe_audio(str(input_wav), source_lang)
        source_text = asr_result["text"]
        detected_language = asr_result["language"]
        confidence = asr_result.get("confidence")
        asr_ms = (perf_counter() - asr_started) * 1000

        effective_source_lang = source_lang or detected_language
        if effective_source_lang == "unknown":
            raise HTTPException(status_code=422, detail="Could not detect source language")
        if effective_source_lang == target_lang:
            raise HTTPException(status_code=400, detail="Source and target languages must be different")
        if (effective_source_lang, target_lang) not in SUPPORTED_PAIRS:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported translation pair: {effective_source_lang}->{target_lang}",
            )

        translation_started = perf_counter()
        translated_text = await _translate_text(source_text, effective_source_lang, target_lang)
        translation_ms = (perf_counter() - translation_started) * 1000

        tts_started = perf_counter()
        await _generate_tts(translated_text, target_lang, str(output_mp3))
        tts_ms = (perf_counter() - tts_started) * 1000

        sentiment, sentiment_score = analyze_sentiment(source_text)
        keywords = extract_keywords(source_text)
        summary = generate_summary(source_text)
        translation_confidence = estimate_translation_confidence(
            confidence, source_text, translated_text
        )

        latency = {
            "asr": round(asr_ms, 2),
            "translation": round(translation_ms, 2),
            "tts": round(tts_ms, 2),
            "total": round((perf_counter() - total_started) * 1000, 2),
        }

        response_data = {
            "source_text": source_text,
            "translated_text": translated_text,
            "audio_url": f"{PUBLIC_BASE_URL}/static/audio/{request_id}.mp3",
            "detected_language": detected_language,
            "confidence": confidence,
            "translation_confidence": translation_confidence,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "keywords": keywords,
            "summary": summary,
            "audio_duration_ms": audio_duration_ms,
            "cached": False,
            "latency": latency,
        }

        translation_cache.set(cache_key, response_data)
        analytics_store.record_translation(
            source_lang=source_lang,
            target_lang=target_lang,
            detected_language=detected_language,
            source_text=source_text,
            translated_text=translated_text,
            confidence=confidence,
            translation_confidence=translation_confidence,
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            keywords=keywords,
            summary=summary,
            latency=latency,
            audio_duration_ms=audio_duration_ms,
            cached=False,
        )
        analytics_store.record_request(
            endpoint="/translate-speech",
            status="success",
            target_lang=target_lang,
            latency_ms=latency["total"],
        )

        return TranslationResponse(**response_data)

    except HTTPException as exc:
        analytics_store.record_request(
            endpoint="/translate-speech",
            status="failure",
            error_message=str(exc.detail),
            target_lang=target_lang,
            latency_ms=round((perf_counter() - total_started) * 1000, 2),
        )
        raise
    except Exception as exc:
        analytics_store.record_request(
            endpoint="/translate-speech",
            status="failure",
            error_message=str(exc),
            target_lang=target_lang,
            latency_ms=round((perf_counter() - total_started) * 1000, 2),
        )
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    finally:
        try:
            input_webm.unlink(missing_ok=True)
            input_wav.unlink(missing_ok=True)
        except OSError:
            pass
