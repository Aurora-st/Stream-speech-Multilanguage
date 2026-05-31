# Git Cleanup Report

**Repository:** `D:\Stream speech`  
**Remote:** https://github.com/Aurora-st/Stream-speech-Multilanguage.git  
**Audit Date:** 2026-05-31  
**Total tracked size (before cleanup):** ~3.12 GB across 53,562 files

---

## Executive Summary

The push failed because **the entire Python virtual environment** (`backend/venv/`, 53,095 files) was committed, along with model weights, generated audio, temp files, and `__pycache__`. GitHub rejects files over 100 MB and warns above 50 MB.

After cleanup, the repository should contain **~150 source/config files** (~5–15 MB total).

---

## Largest Folders (on disk)

| Folder | Size (MB) | Should be in Git? |
|---|---:|---|
| `backend/` (includes venv) | 3,188 | **Partial** — source only |
| `backend/venv/` | ~2,900 | **NO** |
| `backend/pretrained_models/` | ~160 | **NO** — auto-download |
| `streamspeech/` (includes node_modules) | 488 | **Partial** — source only |
| `streamspeech/node_modules/` | ~480 | **NO** |
| `streamspeech/dist/` | ~1.5 | **NO** — build output |
| `backend/temp_audio/` | ~5 | **NO** |
| `backend/static/audio/` | ~2 | **NO** |
| `docs/` | 0.01 | YES |
| `screenshots/` | 0 | YES |

---

## Files Exceeding 100 MB (tracked in Git)

| Size (MB) | Path |
|---:|---|
| 675.84 | `backend/venv/Lib/site-packages/torch/lib/dnnl.lib` |
| 240.50 | `backend/venv/Lib/site-packages/torch/lib/torch_cpu.dll` |
| 207.14 | `backend/venv/Lib/site-packages/sudachidict_core/resources/system.dic` |
| 101.66 | `backend/venv/Lib/site-packages/llvmlite/binding/llvmlite.dll` |

All four are inside `backend/venv/` and must be removed from Git tracking.

---

## Files Exceeding 50 MB (tracked in Git)

| Size (MB) | Path |
|---:|---|
| 675.84 | `backend/venv/.../dnnl.lib` |
| 240.50 | `backend/venv/.../torch_cpu.dll` |
| 207.14 | `backend/venv/.../system.dic` |
| 101.66 | `backend/venv/.../llvmlite.dll` |
| 85.10 | `backend/pretrained_models/hf/hub/.../blobs/f9569...` |
| 83.58 | `backend/venv/.../ffmpeg-win-x86_64-v7.1.exe` |
| 72.07 | `backend/pretrained_models/whisper/tiny.pt` |
| 66.96 | `backend/venv/.../gruut_lang_es/espeak/lexicon.db` |
| 60.95 | `backend/venv/.../gruut_lang_es/lexicon.db` |
| 57.05 | `backend/venv/.../ctranslate2/ctranslate2.dll` |

---

## Tracked File Count by Category

| Category | Files Tracked | Action |
|---|---:|---|
| `backend/venv/` | 53,095 | Remove from Git |
| `backend/static/audio/` | 180 | Remove from Git |
| `backend/temp_audio/` | 89 | Remove from Git |
| `__pycache__/` | 18 | Remove from Git |
| `streamspeech/dist/` | 14 | Remove from Git |
| `backend/pretrained_models/` | 9 | Remove from Git |
| `*.db` (analytics) | 1 | Remove from Git |
| **Source code** | ~156 | **Keep** |

`streamspeech/node_modules/` is **not** tracked (good).

---

## Files That Should NOT Be Committed

| Pattern | Reason |
|---|---|
| `backend/venv/` | Local Python environment; recreate with `pip install` |
| `backend/pretrained_models/` | Model weights; Whisper downloads on first run |
| `**/__pycache__/`, `*.pyc` | Python bytecode |
| `backend/temp_audio/` | Per-request upload scratch |
| `backend/static/audio/` | Generated TTS MP3 output |
| `backend/data/*.db` | Runtime SQLite analytics |
| `streamspeech/dist/` | Vite production build |
| `streamspeech/node_modules/` | npm dependencies |
| `.env` | Secrets / local config |
| `backend/metrics_output/` | Regenerated evaluation charts |
| `*.tsbuildinfo` | TypeScript incremental cache |
| `pnpm-lock.yaml` | Unused lockfile (project uses npm) |

---

## Recommended Exclusions

A root `.gitignore` has been created at `D:\Stream speech\.gitignore` covering all categories above. The existing `streamspeech/.gitignore` is kept for Vite-specific rules but the **root `.gitignore` is authoritative**.

---

## Root Cause

1. No root-level `.gitignore` existed when `git add .` was run.
2. `backend/venv/` was created inside the repo and committed wholesale.
3. Model cache (`pretrained_models/`) and runtime artifacts were committed before ignore rules existed.

---

## Expected Size After Cleanup

| Component | Approx. size |
|---|---:|
| Source code (backend + frontend) | ~2 MB |
| Docs, Docker, config | ~1 MB |
| `package-lock.json` | ~0.2 MB |
| Screenshots (when added) | ~1–2 MB |
| **Total** | **~5–15 MB** |

---

## Model Download Behavior (post-cleanup)

Removing `pretrained_models/` from Git does **not** break the app:

- **Whisper `tiny`**: Downloaded automatically by `whisper.load_model("tiny")` on first backend startup (~72 MB to local cache).
- **HuggingFace / SpeechBrain models**: Only used by optional modules (`noise_reduction.py`, `voice_cloner.py`); not required for the main `/translate-speech` pipeline.
- **Cache location**: `backend/pretrained_models/` (created at runtime via `cache_guard.py`).

See README **First Run** section for setup instructions.
