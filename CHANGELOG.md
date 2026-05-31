# Changelog

All notable changes to StreamSpeech are documented in this file.

## [2.1.0] - 2026-05-31

### Added
- Global exception middleware with structured JSON error responses
- Upload validation (10 MB limit, content-type checking)
- Audio duration tracking and UI display
- Translation confidence estimation
- Request event tracking for success rate analytics
- Dashboard success rate, sentiment pie chart, detected languages panel
- Animated gradient background CSS
- Root `.env.example` consolidated configuration
- `PROJECT_AUDIT.md` complete codebase audit
- `docs/PORTFOLIO.md` resume, LinkedIn, STAR, interview prep guide

### Changed
- Pipeline step renamed: "Synthesizing" (was "Generating Audio")
- Dashboard stat cards now show success rate and most used language
- README rewritten with GitHub badges, hero section, full API docs
- Analytics API extended with success_rate, most_used_language, avg_audio_duration

### Fixed
- README mermaid diagram corruption
- Progress step timing (removed fake post-response step flashes)
- Recording duration timer cleanup on stop/reset

## [2.0.0] - 2026-05-31

### Added

#### Performance
- Singleton Whisper model loading via FastAPI lifespan (loads once at startup)
- Async FastAPI endpoints with `asyncio.to_thread` for ASR, translation, and TTS
- LRU in-memory translation cache with configurable TTL and max entries
- Full audio response caching keyed by SHA-256 hash of audio bytes + language pair
- Cache hit/miss statistics exposed via analytics API

#### Real-Time Experience
- Live transcription preview during recording (Web Speech API)
- Real-time audio waveform visualization using Web Audio AnalyserNode
- Six-stage progress timeline: Recording → Uploading → Transcribing → Translating → Generating Audio → Complete
- Latency breakdown cards (ASR, Translation, TTS, Total)

#### Advanced AI Features
- Language confidence visualization with progress bar
- Automatic language detection badges
- Speech sentiment detection (positive / neutral / negative)
- Keyword extraction from transcriptions
- Transcript summary generation

#### UI/UX
- Enhanced glassmorphism design system with light/dark theme support
- Subtle particle background animation
- Dark/light theme toggle (next-themes)
- Copy buttons for transcript and translation
- Download buttons for translated audio, recording, and transcript
- Improved mobile responsiveness with responsive grids
- Navigation between Recorder and Dashboard pages

#### Analytics Dashboard
- New `/dashboard` route with statistics overview
- Total translations, average latency, cache metrics
- Language usage charts (Recharts bar chart)
- Recent translation history from SQLite persistence
- Sentiment distribution tracking

#### Backend API
- `GET /health` — service health and cache status
- `GET /analytics/stats` — aggregate metrics
- `GET /analytics/history` — recent translation records
- Extended `POST /translate-speech` response with sentiment, keywords, summary, cached flag

#### Deployment
- `backend/Dockerfile` with FFmpeg
- `streamspeech/Dockerfile` with nginx
- `docker-compose.yml` for full-stack deployment
- Environment variable support (`.env.example` for backend and frontend)
- Production nginx SPA routing config

#### Code Quality
- Service layer architecture (`src/services/api.ts`)
- Reusable hooks: `useAudioWaveform`, `useSpeechRecognition`
- Shared TypeScript types (`src/types/translation.ts`)
- Component extraction: ProgressTimeline, CopyButton, DownloadButton, LanguageBadge, SentimentBadge, KeywordTags
- Pydantic response models and proper HTTPException error handling
- SQLite analytics store with structured schema

### Changed
- Upgraded backend from blocking sync handlers to async with thread offload
- Refactored `MicRecorder` to use service layer and extracted hooks
- Replaced inline API calls with typed fetch wrapper
- Updated `ResultCards` with NLP features and latency cards
- README rewritten with architecture diagrams, API docs, deployment guide, and portfolio section
- Backend requirements aligned with actual runtime dependencies

### Fixed
- Whisper confidence now computed from segment logprobs
- Proper HTTP status codes for validation errors (400, 422, 500)
- TypeScript build errors in refactored components
- Theme CSS variables applied for light/dark modes

## [1.0.0] - Prior

- Initial Mini StreamSpeech release
- Basic mic recording, Whisper ASR, Google Translate, gTTS
- Glassmorphism React UI with progress timeline
- FastAPI backend with CORS support
