import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_ROOT = PROJECT_ROOT / "pretrained_models"

HF_CACHE = MODEL_ROOT / "hf"
TORCH_CACHE = MODEL_ROOT / "torch"
SB_CACHE = MODEL_ROOT / "noise_reduction"
TTS_CACHE = MODEL_ROOT / "tts"

# create directories
for p in [HF_CACHE, TORCH_CACHE, SB_CACHE, TTS_CACHE]:
    p.mkdir(parents=True, exist_ok=True)

# FORCE ENV VARIABLES BEFORE ANY MODEL IMPORTS
os.environ["HF_HOME"] = str(HF_CACHE)
os.environ["TRANSFORMERS_CACHE"] = str(HF_CACHE)
os.environ["TORCH_HOME"] = str(TORCH_CACHE)
os.environ["XDG_CACHE_HOME"] = str(MODEL_ROOT)
os.environ["TTS_HOME"] = str(TTS_CACHE)

print("\nMODEL CACHE ROOT:", MODEL_ROOT)
