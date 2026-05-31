# Final GitHub Readiness Checklist

Use this checklist before pushing to GitHub.

---

## Pre-Push Validation

| Check | Command | Expected |
|---|---|---|
| No file > 100 MB tracked | See below | Empty output |
| No file > 50 MB tracked | See below | Empty output |
| venv not tracked | `git ls-files backend/venv \| Measure-Object` | 0 lines |
| node_modules not tracked | `git ls-files streamspeech/node_modules \| Measure-Object` | 0 lines |
| Whisper model not tracked | `git ls-files backend/pretrained_models \| Measure-Object` | 0 lines |
| Generated audio not tracked | `git ls-files backend/static/audio backend/temp_audio \| Measure-Object` | 0 lines |
| Root .gitignore exists | `Test-Path .gitignore` | True |
| Tracked file count reasonable | `git ls-files \| Measure-Object` | < 300 lines |
| Total tracked size | See below | < 20 MB |

### Validation commands (PowerShell)

```powershell
cd "D:\Stream speech"

# Files over 100 MB
git ls-files | ForEach-Object { if (Test-Path $_) { $s=(Get-Item $_).Length; if ($s -gt 100MB) { "$([math]::Round($s/1MB,2)) MB  $_" } } }

# Files over 50 MB
git ls-files | ForEach-Object { if (Test-Path $_) { $s=(Get-Item $_).Length; if ($s -gt 50MB) { "$([math]::Round($s/1MB,2)) MB  $_" } } }

# Total tracked size
$total = (git ls-files | ForEach-Object { if (Test-Path $_) { (Get-Item $_).Length } else { 0 } } | Measure-Object -Sum).Sum
"Total tracked: $([math]::Round($total/1MB,2)) MB"

# Category checks
"venv:        $((git ls-files backend/venv | Measure-Object).Count)"
"models:      $((git ls-files backend/pretrained_models | Measure-Object).Count)"
"node_modules:$((git ls-files streamspeech/node_modules | Measure-Object).Count)"
"dist:        $((git ls-files streamspeech/dist | Measure-Object).Count)"
"temp_audio:  $((git ls-files backend/temp_audio | Measure-Object).Count)"
"static_audio:$((git ls-files backend/static/audio | Measure-Object).Count)"
"total files: $((git ls-files | Measure-Object).Count)"
```

---

## Build Safety (after cleanup)

| Component | Still works? | Notes |
|---|---|---|
| Backend startup | ✅ | Uses local `backend/venv/` (not in Git) |
| Frontend dev | ✅ | Uses local `node_modules/` (not in Git) |
| Docker build | ✅ | Installs deps inside container |
| Whisper ASR | ✅ | Downloads `tiny` model on first run |
| README instructions | ✅ | Updated with first-run model note |

---

## Files to Commit After Cleanup

- [ ] `.gitignore` (root)
- [ ] `GIT_CLEANUP_REPORT.md`
- [ ] `REMOVE_TRACKED_FILES.md`
- [ ] `FINAL_GITHUB_CHECKLIST.md`
- [ ] `PUSH_TO_GITHUB.md`
- [ ] Deletion of cached venv/models/audio from Git index

---

## Post-Push Verification

- [ ] GitHub repo size shows < 50 MB
- [ ] Clone on fresh machine + `pip install` + `npm install` works
- [ ] No GitHub "large file" warning on push
- [ ] `.env` not visible in repository

---

## Status (after cleanup — 2026-05-31)

| Item | Status |
|---|---|
| `.gitignore` created | ✅ |
| `git rm --cached` executed | ✅ |
| Tracked files | **151** (was 53,562) |
| Tracked size | **1.02 MB** (was 3.12 GB) |
| Files > 50 MB | **0** |
| Files > 100 MB | **0** |
| Commit created | ⬜ Pending |
| Push succeeded | ⬜ Pending |
