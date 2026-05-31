from __future__ import annotations

import re

import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

try:
    from .schemas import Language
except ImportError:  # Allows running as `uvicorn main:app` from backend dir.
    from schemas import Language

SUPPORTED_LANGUAGE_PAIRS = {
    (Language.JA.value, Language.EN.value): "Helsinki-NLP/opus-mt-ja-en",
    (Language.EN.value, Language.JA.value): "Helsinki-NLP/opus-mt-en-jap",
    (Language.HI.value, Language.EN.value): "Helsinki-NLP/opus-mt-hi-en",
    (Language.EN.value, Language.HI.value): "Helsinki-NLP/opus-mt-en-hi",
}

_tokenizers: dict[tuple[str, str], AutoTokenizer] = {}
_models: dict[tuple[str, str], AutoModelForSeq2SeqLM] = {}


def _normalize_text(text: str) -> str:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return ""
    return cleaned[0].upper() + cleaned[1:]


def load_translator() -> None:
    """Load all supported MarianMT models once (call from app lifespan)."""
    if _tokenizers and _models:
        return
    for pair, model_name in SUPPORTED_LANGUAGE_PAIRS.items():
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
        model.eval()
        _tokenizers[pair] = tokenizer
        _models[pair] = model


def get_model_name(source_lang: str, target_lang: str) -> str:
    return SUPPORTED_LANGUAGE_PAIRS.get((source_lang, target_lang), "unknown-model")


def translate_text(source_text: str, source_lang: str, target_lang: str) -> str:
    if not source_text or not source_text.strip():
        return ""
    pair = (source_lang, target_lang)
    tokenizer = _tokenizers.get(pair)
    model = _models.get(pair)
    if tokenizer is None or model is None:
        supported_pairs = ", ".join(
            f"{src}->{tgt}" for src, tgt in sorted(SUPPORTED_LANGUAGE_PAIRS.keys())
        )
        raise ValueError(
            f"Unsupported translation pair: {source_lang} -> {target_lang}. "
            f"Supported pairs: {supported_pairs}"
        )
    print("Using model:", get_model_name(source_lang, target_lang))
    inputs = tokenizer(
        source_text,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=512,
    )
    with torch.no_grad():
        generated = model.generate(**inputs, max_length=512)
    decoded = tokenizer.decode(generated[0], skip_special_tokens=True)
    return _normalize_text(decoded)
