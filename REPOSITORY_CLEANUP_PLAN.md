# Repository Cleanup Plan

**Goal:** GitHub-ready source repository (~5–15 MB) that remains fully functional locally.

---

## Folders & Files That SHOULD Remain in Git

```
D:\Stream speech\
├── .gitignore                    # Root ignore rules (NEW)
├── .env.example                  # Environment template
├── README.md
├── CHANGELOG.md
├── IMPLEMENTATION_REPORT.md
├── PROJECT_AUDIT.md
├── GIT_CLEANUP_REPORT.md
├── REMOVE_TRACKED_FILES.md
├── FINAL_GITHUB_CHECKLIST.md
├── PUSH_TO_GITHUB.md
├── docker-compose.yml
├── docs/
│   ├── ARCHITECTURE.md
│   └── PORTFOLIO.md
├── screenshots/
│   └── README.md
├── backend/
│   ├── main.py, config.py, cache.py, analytics.py, ...
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── .env.example
│   └── (source .py files only)
└── streamspeech/
    ├── src/, components/, public/
    ├── package.json, package-lock.json
    ├── vite.config.ts, tsconfig.json
    ├── Dockerfile, nginx.conf
    └── .env.example
```

---

## Folders That Should NEVER Be Pushed

| Path | Size | Why excluded |
|---|---|---|
| `backend/venv/` | ~2.9 GB | Recreate with `pip install -r requirements.txt` |
| `backend/pretrained_models/` | ~160 MB | Whisper/HF models auto-download on first run |
| `streamspeech/node_modules/` | ~480 MB | Recreate with `npm install` |
| `streamspeech/dist/` | ~1.5 MB | Recreate with `npm run build` |
| `backend/temp_audio/` | ~5 MB | Runtime upload scratch |
| `backend/static/audio/` | ~2 MB | Generated TTS output |
| `backend/data/` | varies | Runtime SQLite analytics |
| `backend/__pycache__/` | small | Python bytecode |
| `backend/metrics_output/` | small | Regenerated charts |
| `.env` | tiny | Local secrets |

---

## Cleanup Steps (in order)

1. ✅ Create root `.gitignore`
2. ⬜ Run `git rm -r --cached` commands (see `REMOVE_TRACKED_FILES.md`)
3. ⬜ Commit cleanup changes
4. ⬜ Validate no file > 100 MB tracked
5. ⬜ Push to GitHub (or fresh init per `PUSH_TO_GITHUB.md`)

---

## Post-Cleanup Local Setup (for new clones)

```powershell
# Backend
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
# First run downloads Whisper tiny (~72 MB) automatically
uvicorn main:app --reload --port 8000

# Frontend
cd streamspeech
npm install
npm run dev
```

---

## Docker (unaffected by cleanup)

Docker builds install dependencies inside containers — no local venv or node_modules needed for deployment:

```powershell
docker compose up --build
```
