import os
import re
import uuid
from pathlib import Path

import torch
from pydub import AudioSegment
from TTS.api import TTS

BASE_DIR = Path(__file__).resolve().parent
PRETRAINED_DIR = BASE_DIR / "pretrained_models"
TTS_CACHE_DIR = PRETRAINED_DIR / "tts"
HF_CACHE_DIR = PRETRAINED_DIR / "hf"
TORCH_CACHE_DIR = PRETRAINED_DIR / "torch"

for cache_dir in (TTS_CACHE_DIR, HF_CACHE_DIR, TORCH_CACHE_DIR):
    cache_dir.mkdir(parents=True, exist_ok=True)

os.environ.setdefault("TTS_HOME", str(TTS_CACHE_DIR))
os.environ.setdefault("HF_HOME", str(HF_CACHE_DIR))
os.environ.setdefault("TORCH_HOME", str(TORCH_CACHE_DIR))

device = "cuda" if torch.cuda.is_available() else "cpu"

print("Loading XTTS voice cloning model (first run downloads ~2GB)...")

tts_model = TTS(
    model_name="tts_models/multilingual/multi-dataset/xtts_v2",
    progress_bar=False,
).to(device)

AUDIO_DIR = BASE_DIR / "static" / "audio"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

LANG_MAP = {
    "en": "en",
    "hi": "hi",
    "ja": "ja",
}


def split_sentences(text: str):
    sentences = re.split(r"(?<=[.!?]) +", text)
    return [s.strip() for s in sentences if s.strip()]


def clone_voice_and_generate_speech(text: str, speaker_wav: str, lang: str):
    """
    Generate speech using cloned voice from speaker_wav.
    Returns public URL of mp3 file.
    """
    lang_code = LANG_MAP.get(lang, "en")
    file_id = str(uuid.uuid4())
    mp3_path = AUDIO_DIR / f"{file_id}.mp3"

    sentences = split_sentences(text)
    combined_audio = AudioSegment.empty()

    for sentence in sentences:
        temp_wav = AUDIO_DIR / f"temp_{uuid.uuid4()}.wav"

        tts_model.tts_to_file(
            text=sentence,
            speaker_wav=speaker_wav,
            language=lang_code,
            file_path=str(temp_wav),
            temperature=0.65,
            speed=1.0,
        )

        combined_audio += AudioSegment.from_wav(str(temp_wav))
        os.remove(temp_wav)

    combined_audio.export(str(mp3_path), format="mp3")

    return f"http://localhost:8000/static/audio/{file_id}.mp3"
