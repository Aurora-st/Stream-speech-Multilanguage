# GitHub Recovery Guide

**Repository:** https://github.com/Aurora-st/Stream-speech-Multilanguage.git  
**Local root:** `D:\Stream speech`

---

## Why Push Failed

GitHub rejects pushes when **any blob in Git history** exceeds 100 MB. Even after removing files from tracking with `git rm --cached`, the old commits still contain:

| Size | File in history |
|---:|---|
| 675 MB | `backend/venv/.../dnnl.lib` |
| 240 MB | `backend/venv/.../torch_cpu.dll` |
| 207 MB | `backend/venv/.../system.dic` |
| 101 MB | `backend/venv/.../llvmlite.dll` |
| 85 MB | `backend/pretrained_models/.../speechbrain blob` |
| 72 MB | `backend/pretrained_models/whisper/tiny.pt` |

**Current index is clean** (1.04 MB, 157 files), but **history is not**. A fresh Git init is required.

---

## Current Git Audit (Index — Clean ✅)

| Check | Result |
|---|---|
| Tracked files | 157 |
| Tracked size | **1.04 MB** |
| Files > 100 MB | **0** |
| Files > 50 MB | **0** |
| `backend/venv/` tracked | **0** |
| `backend/pretrained_models/` tracked | **0** |
| `streamspeech/node_modules/` tracked | **0** |
| `backend/temp_audio/` tracked | **0** |
| `backend/static/audio/` tracked | **0** |
| Root `.gitignore` | ✅ Present |

---

## Recovery — Fresh Git History (Recommended)

Run these commands in PowerShell from the repository root:

```powershell
cd "D:\Stream speech"

# Step 1: Remove old Git history (contains 675 MB blobs)
Remove-Item -Recurse -Force .git

# Step 2: Initialize fresh repository
git init

# Step 3: Stage all files (.gitignore excludes venv, models, etc.)
git add .

# Step 4: Verify nothing large is staged
git ls-files | ForEach-Object {
  if (Test-Path $_) {
    $s = (Get-Item $_).Length
    if ($s -gt 50MB) { Write-Output "WARNING: $([math]::Round($s/1MB,2)) MB  $_" }
  }
}
# Expected: no output

# Step 5: Verify file count
(git ls-files | Measure-Object).Count
# Expected: ~160 files (not 53,000+)

# Step 6: Initial commit
git commit -m "Initial commit: StreamSpeech multilingual AI translation platform"

# Step 7: Set branch and remote
git branch -M main
git remote add origin https://github.com/Aurora-st/Stream-speech-Multilanguage.git

# Step 8: Push (force required if remote has old large history)
git push -u origin main --force
```

---

## Why This Is Safe

| Concern | Answer |
|---|---|
| Will I lose my code? | **No.** Only `.git/` (history metadata) is deleted. All source files remain. |
| Will I lose venv/models? | **No.** They stay on disk; they were never meant to be in Git. |
| Will the app still run? | **Yes.** Backend uses local `venv/`, frontend uses local `node_modules/`. |
| What is removed? | Old commit history containing 3+ GB of accidental commits. |
| What is preserved? | All source code, docs, Docker files, configs, README, screenshots folder. |

---

## What Data Is Preserved (on disk)

```
D:\Stream speech\
├── backend/venv/              ← Python environment (local only)
├── backend/pretrained_models/ ← Whisper/model cache (local only)
├── backend/static/audio/      ← Generated MP3s (local only)
├── backend/temp_audio/        ← Temp uploads (local only)
├── streamspeech/node_modules/ ← npm packages (local only)
├── streamspeech/dist/         ← Build output (local only)
└── All source .py, .tsx, .ts, docs, Docker files
```

---

## What Data Is Removed

- `.git/` folder — entire commit history with embedded 675 MB Torch DLLs
- Remote GitHub history (replaced on force push)

---

## After Push — Clone Test

```powershell
cd D:\temp
git clone https://github.com/Aurora-st/Stream-speech-Multilanguage.git test-clone
cd test-clone\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
# First run downloads Whisper tiny (~72 MB) automatically
```

---

## If You Prefer Not to Force Push

Create a new GitHub repository with a different name and push there without `--force`. Same local commands, different remote URL.

---

## Related Documents

- `GIT_CLEANUP_REPORT.md` — Full size audit
- `REMOVE_TRACKED_FILES.md` — `git rm --cached` commands (already executed)
- `FINAL_GITHUB_CHECKLIST.md` — Pre-push validation
- `.gitignore` — Root ignore rules
