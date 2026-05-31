# Push to GitHub — Exact Commands

**Repository:** https://github.com/Aurora-st/Stream-speech-Multilanguage.git  
**Local root:** `D:\Stream speech`

---

## Before You Push

1. Run commands in `REMOVE_TRACKED_FILES.md` to untrack large files.
2. Verify with `FINAL_GITHUB_CHECKLIST.md`.
3. Choose Option A or B below.

---

## Option A — Fresh History (Recommended)

**Best when:** Push failed due to large files already in Git history (3+ GB blobs remain even after `git rm --cached`).

**Pros:**
- Smallest repo size on GitHub immediately
- No large blobs in history
- Clean "Initial commit" for portfolio

**Cons:**
- Loses previous commit history
- Force push required if remote already has commits

### Commands (PowerShell)

```powershell
cd "D:\Stream speech"

# 1. Ensure .gitignore exists (already created at repo root)

# 2. Remove old Git history
Remove-Item -Recurse -Force .git

# 3. Initialize fresh repository
git init
git add .
git status
# Confirm: NO backend/venv, NO pretrained_models, NO temp_audio, NO dist

# 4. Initial commit
git commit -m "Initial commit: StreamSpeech multilingual AI translation platform"

# 5. Set main branch and remote
git branch -M main
git remote add origin https://github.com/Aurora-st/Stream-speech-Multilanguage.git

# 6. Push (force if remote has old large history)
git push -u origin main
```

If remote rejects because it has old history:

```powershell
git push -u origin main --force
```

> ⚠️ Only use `--force` if you intend to replace the remote history entirely.

---

## Option B — Keep History, Clean Tracked Files

**Best when:** History is small and you want to preserve commits.

**Pros:**
- Keeps commit history and messages
- Safer for collaborative repos

**Cons:**
- **Large blobs may remain in old commits** — GitHub can still reject push
- Repo size on GitHub stays inflated unless you run `git filter-repo` or BFG

### Commands (PowerShell)

```powershell
cd "D:\Stream speech"

# 1. Untrack large/generated files (keep local copies)
git rm -r --cached backend/venv/
git rm -r --cached backend/pretrained_models/
git rm -r --cached backend/__pycache__/
git rm -r --cached backend/temp_audio/
git rm -r --cached backend/static/audio/
git rm -r --cached backend/data/
git rm -r --cached streamspeech/dist/
git rm -r --cached backend/metrics_output/
git rm --cached pnpm-lock.yaml 2>$null
git rm --cached streamspeech/tsconfig.tsbuildinfo 2>$null

# 2. Stage ignore rules and docs
git add .gitignore
git add GIT_CLEANUP_REPORT.md REMOVE_TRACKED_FILES.md FINAL_GITHUB_CHECKLIST.md PUSH_TO_GITHUB.md

# 3. Commit
git commit -m "Remove venv, models, and generated files from tracking; add root .gitignore"

# 4. Push
git push -u origin main
```

### If Option B push still fails

Git history still contains the 675 MB `dnnl.lib` and other blobs. You must either:

1. **Switch to Option A** (fresh init — easiest), or
2. Run **BFG Repo-Cleaner** / **git filter-repo** to purge blobs from history

---

## Comparison

| | Option A (Fresh init) | Option B (Keep history) |
|---|---|---|
| Effort | Low | Medium |
| GitHub size | Minimal (~5–15 MB) | May stay large |
| Push success | Very likely | May fail if blobs in history |
| History preserved | No | Yes |
| **Recommended for this repo** | ✅ **Yes** | Only if history matters |

---

## After Successful Push

Verify on GitHub:

1. Repository size < 50 MB (Settings → scroll to bottom)
2. No `backend/venv/` folder visible
3. No `pretrained_models/` folder visible
4. README renders correctly

Clone test on another machine:

```powershell
git clone https://github.com/Aurora-st/Stream-speech-Multilanguage.git
cd Stream-speech-Multilanguage/backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --port 8000
```

First backend start downloads Whisper `tiny` automatically (~72 MB).

---

## Troubleshooting

| Error | Fix |
|---|---|
| `File exceeds 100 MB` | Use Option A or BFG/filter-repo |
| `remote rejected` | Force push after Option A: `git push -u origin main --force` |
| `venv/` still in `git status` | Confirm root `.gitignore` exists; run `git rm -r --cached backend/venv/` |
| Models missing after clone | Normal — run backend once; Whisper auto-downloads |
