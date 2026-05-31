"""Lightweight NLP utilities: sentiment, keywords, and summarization."""

from __future__ import annotations

import re
from collections import Counter

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with",
    "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "do", "does",
    "did", "will", "would", "could", "should", "may", "might", "must", "shall", "can",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her", "us", "them", "my",
    "your", "his", "its", "our", "their", "this", "that", "these", "those", "am", "not",
    "so", "if", "then", "than", "too", "very", "just", "about", "into", "from", "as",
}

POSITIVE_WORDS = {
    "good", "great", "excellent", "happy", "love", "wonderful", "amazing", "fantastic",
    "beautiful", "best", "nice", "thanks", "thank", "perfect", "awesome", "glad", "joy",
    "success", "positive", "helpful", "brilliant", "delight", "pleased", "fine", "well",
}

NEGATIVE_WORDS = {
    "bad", "terrible", "awful", "sad", "hate", "horrible", "worst", "angry", "upset",
    "fail", "failed", "problem", "wrong", "pain", "hurt", "disappoint", "negative",
    "poor", "difficult", "hard", "annoy", "frustrat", "worry", "anxious", "fear",
}


def _tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z\u0900-\u097F\u3040-\u30FF\u4E00-\u9FFF]+", text.lower())


def analyze_sentiment(text: str) -> tuple[str, float]:
    if not text.strip():
        return "neutral", 0.5

    tokens = _tokenize(text)
    if not tokens:
        return "neutral", 0.5

    pos = sum(1 for t in tokens if t in POSITIVE_WORDS)
    neg = sum(1 for t in tokens if any(t.startswith(n) for n in NEGATIVE_WORDS))

    if pos == 0 and neg == 0:
        return "neutral", 0.5

    score = (pos + 1) / (pos + neg + 2)
    if score >= 0.6:
        label = "positive"
    elif score <= 0.4:
        label = "negative"
    else:
        label = "neutral"
    return label, round(score, 3)


def extract_keywords(text: str, max_keywords: int = 8) -> list[str]:
    if not text.strip():
        return []

    tokens = [t for t in _tokenize(text) if len(t) > 2 and t not in STOPWORDS]
    if not tokens:
        return []

    counts = Counter(tokens)
    return [word for word, _ in counts.most_common(max_keywords)]


def estimate_translation_confidence(
    asr_confidence: float | None,
    source_text: str,
    translated_text: str,
) -> float:
    """Heuristic translation confidence based on ASR confidence and output quality."""
    base = asr_confidence if asr_confidence is not None else 0.72
    if not translated_text.strip():
        return round(base * 0.3, 3)
    if not source_text.strip():
        return round(base * 0.5, 3)
    length_ratio = min(len(translated_text), len(source_text)) / max(len(source_text), 1)
    ratio_factor = 0.85 + min(length_ratio, 1.0) * 0.15
    return round(min(0.98, base * ratio_factor), 3)


def generate_summary(text: str, max_sentences: int = 2) -> str:
    cleaned = text.strip()
    if not cleaned:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", cleaned)
    sentences = [s.strip() for s in sentences if s.strip()]
    if not sentences:
        return cleaned[:160] + ("..." if len(cleaned) > 160 else "")

    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    return " ".join(sentences[:max_sentences])
