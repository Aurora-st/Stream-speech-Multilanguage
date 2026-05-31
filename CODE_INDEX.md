# Code Index (StreamSpeech)

This document acts as an index to explain the JavaScript/TypeScript frontend and the Python backend code in this repository.

> Note: Your request said “make a readme explaining all the codes in js and index all code”. The repo contains **JS/TS frontend** and **Python backend**. Below I index **JS/TS thoroughly** and also include a concise index for backend files so the overall flow is understandable.

---

## Frontend (JS/TS) - Vite + React

### Entry points
- `streamspeech/index.html`
  - HTML shell for the Vite app.
  - Loads `/src/main.tsx`.
- `streamspeech/src/main.tsx`
  - Mounts `App` (React root render).
- `streamspeech/src/App.tsx`
  - Main UI component for the React/Vite app.
  - Renders header, the `MicRecorder`, and footer.

### UI components
- `streamspeech/components/mic-recorder.tsx`
  - Core client logic.
  - Records microphone audio using `MediaRecorder`.
  - Optionally shows live transcript using the browser `SpeechRecognition` API.
  - Sends recorded audio to backend endpoint `POST /translate-speech`.
  - Receives `source_text`, `translated_text`, and `audio_url`.
  - Plays translated MP3 audio via an `<audio>` element.
  - Tracks processing states (`listening → transcribing → translating → generating`).
  - Handles language selection validation (supported pairs).
- `streamspeech/components/result-cards.tsx`
  - Displays:
    - recognized speech (source text)
    - translated output
    - detected language and confidence (if provided)
    - latency breakdown (if provided)
- `streamspeech/components/wave-animation.tsx`
  - Simple animated “sound bars” shown while recording.

### Styling & utilities
- `streamspeech/src/index.css`
  - Tailwind layers + CSS keyframes for wave animation.
- `streamspeech/app/globals.css`
  - Additional Tailwind/CSS variables for a Next-style theme setup.
  - (This repo appears to mix Vite and Next directories; actual runtime depends on tooling.)
- `streamspeech/lib/utils.ts`
  - `cn()` helper: merges Tailwind class strings using `clsx` + `tailwind-merge`.

### Config / build system
- `streamspeech/vite.config.ts`
  - Vite + React plugin.
  - Sets `@` alias to the project root.
  - Dev server port is fixed to `5173`.
- `streamspeech/package.json`
  - Frontend dependencies (React, Tailwind, shadcn/ui/Radix UI, axios, lucide, sonner, etc.)

---

## Backend (Python) - FastAPI

The frontend calls the backend endpoint below:
- `POST /translate-speech`

Key backend files:
- `backend/main.py`
  - FastAPI server.
  - Loads Whisper model at startup.
  - Implements `/translate-speech`:
    1. Save uploaded audio to `temp_audio/`
    2. Convert WebM → WAV via `audio_convert.py`
    3. Transcribe with Whisper
    4. Translate with `googletrans`
    5. Convert translated text to MP3 using `gTTS`
    6. Return `audio_url` pointing at `static/audio/<request_id>.mp3`
- `backend/audio_convert.py`
  - Resolves FFmpeg executable and converts media.
  - Contains `convert_webm_to_wav()`.
- `backend/whisper_asr.py`
  - Helper wrapper around `faster_whisper` (note: `main.py` uses `openai-whisper` directly in the code shown).
- `backend/translator.py`
  - MarianMT/Transformers-based translation helper (note: `main.py` currently uses `googletrans` directly).
- `backend/voice_cloner.py`
  - XTTS voice cloning helper using `TTS` library (not wired in the shown `main.py`).
- `backend/schemas.py`
  - Pydantic models/enums used for typing/validation.

---

## Recommended documentation strategy

1. Keep frontend docs close to the components.
2. Explain the end-to-end request/response flow once.
3. Then document each file with:
   - purpose
   - key functions/components
   - input/output and side effects

---

## End-to-end flow (what happens when you press Record)

1. `MicRecorder` records audio into a `Blob`.
2. It posts `FormData` to `http://localhost:8000/translate-speech`.
3. Backend converts audio → transcribes → translates → generates MP3.
4. Backend returns JSON containing an `audio_url`.
5. Frontend updates UI and plays the MP3.

