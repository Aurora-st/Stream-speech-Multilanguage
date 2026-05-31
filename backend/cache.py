"""In-memory LRU cache for translation results."""

from __future__ import annotations

import hashlib
import time
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any

from config import CACHE_MAX_ENTRIES, CACHE_TTL_SECONDS


@dataclass
class CacheEntry:
    value: dict[str, Any]
    created_at: float


class TranslationCache:
    def __init__(self, max_entries: int = CACHE_MAX_ENTRIES, ttl_seconds: int = CACHE_TTL_SECONDS) -> None:
        self._max_entries = max_entries
        self._ttl_seconds = ttl_seconds
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0

    @staticmethod
    def _hash_key(*parts: str) -> str:
        payload = "|".join(parts).encode("utf-8")
        return hashlib.sha256(payload).hexdigest()

    def make_audio_key(self, audio_bytes: bytes, source_lang: str | None, target_lang: str) -> str:
        audio_hash = hashlib.sha256(audio_bytes).hexdigest()
        return self._hash_key(audio_hash, source_lang or "auto", target_lang)

    def make_text_key(self, text: str, source_lang: str, target_lang: str) -> str:
        return self._hash_key(text.strip().lower(), source_lang, target_lang)

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._store.get(key)
        if entry is None:
            self.misses += 1
            return None
        if time.time() - entry.created_at > self._ttl_seconds:
            del self._store[key]
            self.misses += 1
            return None
        self._store.move_to_end(key)
        self.hits += 1
        return entry.value

    def set(self, key: str, value: dict[str, Any]) -> None:
        if key in self._store:
            del self._store[key]
        self._store[key] = CacheEntry(value=value, created_at=time.time())
        while len(self._store) > self._max_entries:
            self._store.popitem(last=False)

    def stats(self) -> dict[str, int | float]:
        total = self.hits + self.misses
        hit_rate = (self.hits / total * 100) if total else 0.0
        return {
            "entries": len(self._store),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate_percent": round(hit_rate, 2),
        }


translation_cache = TranslationCache()
