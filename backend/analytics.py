"""SQLite analytics persistence for translation history and metrics."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from uuid import uuid4

from config import DATABASE_PATH


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AnalyticsStore:
    def __init__(self, db_path: Path = DATABASE_PATH) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS translations (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    source_lang TEXT,
                    target_lang TEXT NOT NULL,
                    detected_language TEXT,
                    source_text TEXT,
                    translated_text TEXT,
                    confidence REAL,
                    translation_confidence REAL,
                    sentiment TEXT,
                    sentiment_score REAL,
                    keywords TEXT,
                    summary TEXT,
                    latency_asr REAL,
                    latency_translation REAL,
                    latency_tts REAL,
                    latency_total REAL,
                    audio_duration_ms REAL,
                    cached INTEGER DEFAULT 0
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS request_events (
                    id TEXT PRIMARY KEY,
                    created_at TEXT NOT NULL,
                    endpoint TEXT NOT NULL,
                    status TEXT NOT NULL,
                    error_message TEXT,
                    target_lang TEXT,
                    latency_ms REAL
                )
                """
            )
            # Migrate older databases
            cols = {row[1] for row in conn.execute("PRAGMA table_info(translations)").fetchall()}
            if "translation_confidence" not in cols:
                conn.execute("ALTER TABLE translations ADD COLUMN translation_confidence REAL")

    def record_request(
        self,
        *,
        endpoint: str,
        status: str,
        error_message: str | None = None,
        target_lang: str | None = None,
        latency_ms: float | None = None,
    ) -> str:
        record_id = uuid4().hex
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO request_events (id, created_at, endpoint, status, error_message, target_lang, latency_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (record_id, _utc_now(), endpoint, status, error_message, target_lang, latency_ms),
            )
        return record_id

    def record_translation(
        self,
        *,
        source_lang: str | None,
        target_lang: str,
        detected_language: str,
        source_text: str,
        translated_text: str,
        confidence: float | None,
        translation_confidence: float | None,
        sentiment: str,
        sentiment_score: float,
        keywords: list[str],
        summary: str,
        latency: dict[str, float],
        audio_duration_ms: float | None = None,
        cached: bool = False,
    ) -> str:
        record_id = uuid4().hex
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO translations (
                    id, created_at, source_lang, target_lang, detected_language,
                    source_text, translated_text, confidence, translation_confidence,
                    sentiment, sentiment_score, keywords, summary,
                    latency_asr, latency_translation, latency_tts,
                    latency_total, audio_duration_ms, cached
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record_id,
                    _utc_now(),
                    source_lang,
                    target_lang,
                    detected_language,
                    source_text,
                    translated_text,
                    confidence,
                    translation_confidence,
                    sentiment,
                    sentiment_score,
                    json.dumps(keywords),
                    summary,
                    latency.get("asr"),
                    latency.get("translation"),
                    latency.get("tts"),
                    latency.get("total"),
                    audio_duration_ms,
                    1 if cached else 0,
                ),
            )
        return record_id

    def get_stats(self) -> dict[str, Any]:
        with self._connect() as conn:
            total = conn.execute("SELECT COUNT(*) AS c FROM translations").fetchone()["c"]
            avg_latency = conn.execute(
                "SELECT AVG(latency_total) AS avg_total FROM translations"
            ).fetchone()["avg_total"]
            avg_asr = conn.execute("SELECT AVG(latency_asr) AS v FROM translations").fetchone()["v"]
            avg_translation = conn.execute(
                "SELECT AVG(latency_translation) AS v FROM translations"
            ).fetchone()["v"]
            avg_tts = conn.execute("SELECT AVG(latency_tts) AS v FROM translations").fetchone()["v"]
            avg_duration = conn.execute(
                "SELECT AVG(audio_duration_ms) AS v FROM translations WHERE audio_duration_ms IS NOT NULL"
            ).fetchone()["v"]
            cached_count = conn.execute(
                "SELECT COUNT(*) AS c FROM translations WHERE cached = 1"
            ).fetchone()["c"]

            total_requests = conn.execute("SELECT COUNT(*) AS c FROM request_events").fetchone()["c"]
            success_requests = conn.execute(
                "SELECT COUNT(*) AS c FROM request_events WHERE status = 'success'"
            ).fetchone()["c"]
            failed_requests = conn.execute(
                "SELECT COUNT(*) AS c FROM request_events WHERE status = 'failure'"
            ).fetchone()["c"]

            language_rows = conn.execute(
                """
                SELECT target_lang AS lang, COUNT(*) AS count
                FROM translations
                GROUP BY target_lang
                ORDER BY count DESC
                """
            ).fetchall()
            detected_rows = conn.execute(
                """
                SELECT detected_language AS lang, COUNT(*) AS count
                FROM translations
                WHERE detected_language IS NOT NULL AND detected_language != ''
                GROUP BY detected_language
                ORDER BY count DESC
                """
            ).fetchall()
            sentiment_rows = conn.execute(
                """
                SELECT sentiment, COUNT(*) AS count
                FROM translations
                GROUP BY sentiment
                """
            ).fetchall()

        success_rate = round((success_requests / total_requests) * 100, 2) if total_requests else 100.0
        most_used = language_rows[0]["lang"] if language_rows else None

        return {
            "total_translations": total,
            "average_latency_ms": round(avg_latency or 0, 2),
            "average_audio_duration_ms": round(avg_duration or 0, 2),
            "average_latency_breakdown": {
                "asr": round(avg_asr or 0, 2),
                "translation": round(avg_translation or 0, 2),
                "tts": round(avg_tts or 0, 2),
                "total": round(avg_latency or 0, 2),
            },
            "cached_responses": cached_count,
            "success_rate_percent": success_rate,
            "total_requests": total_requests,
            "failed_requests": failed_requests,
            "most_used_language": most_used,
            "languages_used": [{"lang": r["lang"], "count": r["count"]} for r in language_rows],
            "detected_languages": [{"lang": r["lang"], "count": r["count"]} for r in detected_rows],
            "sentiment_distribution": [
                {"sentiment": r["sentiment"], "count": r["count"]} for r in sentiment_rows
            ],
        }

    def get_history(self, limit: int = 20) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM translations
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        results: list[dict[str, Any]] = []
        for row in rows:
            results.append(
                {
                    "id": row["id"],
                    "created_at": row["created_at"],
                    "source_lang": row["source_lang"],
                    "target_lang": row["target_lang"],
                    "detected_language": row["detected_language"],
                    "source_text": row["source_text"],
                    "translated_text": row["translated_text"],
                    "confidence": row["confidence"],
                    "translation_confidence": row["translation_confidence"],
                    "sentiment": row["sentiment"],
                    "sentiment_score": row["sentiment_score"],
                    "keywords": json.loads(row["keywords"] or "[]"),
                    "summary": row["summary"],
                    "audio_duration_ms": row["audio_duration_ms"],
                    "latency": {
                        "asr": row["latency_asr"],
                        "translation": row["latency_translation"],
                        "tts": row["latency_tts"],
                        "total": row["latency_total"],
                    },
                    "cached": bool(row["cached"]),
                }
            )
        return results


analytics_store = AnalyticsStore()
