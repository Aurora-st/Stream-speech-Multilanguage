# React Bug Fix Report

**Date:** 2026-05-31  
**Issue:** `ReferenceError: ttsAudioRef is not defined`  
**Component:** `streamspeech/components/mic-recorder.tsx`

---

## Root Cause

During a refactor that added recording duration tracking (`recordingTimerRef`, `recordingStartedAtRef`), the `ttsAudioRef` declaration was **accidentally removed** while its usages remained:

| Line | Usage |
|---|---|
| 84–88 | `useEffect` auto-plays translated TTS audio via `ttsAudioRef.current` |
| 332 | `<audio ref={ttsAudioRef} ...>` |

React hooks run on mount; the `useEffect` at line 84 executed immediately and threw `ReferenceError` because `ttsAudioRef` was never declared with `useRef`.

**Note:** The error stack referenced `streamspeech/src/components/mic-recorder.tsx`, but the active file is `streamspeech/components/mic-recorder.tsx` (imported via `@/components/mic-recorder` alias). There is no duplicate file under `src/components/`.

---

## Fix Applied

### 1. Restored `ttsAudioRef` declaration

```typescript
const ttsAudioRef = useRef<HTMLAudioElement | null>(null)
```

Placed alongside all other refs in a dedicated block (lines 39–45):

```typescript
const mediaRecorderRef = useRef<MediaRecorder | null>(null)
const chunksRef = useRef<Blob[]>([])
const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
const recordedMimeRef = useRef<string>("audio/webm")
const recordingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
const recordingStartedAtRef = useRef<number | null>(null)
const ttsAudioRef = useRef<HTMLAudioElement | null>(null)
```

### 2. Added TypeScript environment types

Created `streamspeech/src/vite-env.d.ts` with:

- `ImportMeta.env` for `VITE_API_URL` in `api.ts`
- Web Speech API types (`SpeechRecognitionEvent`, etc.) for `useSpeechRecognition.ts`

Updated `tsconfig.json` to include `src/vite-env.d.ts`.

---

## Files Changed

| File | Change |
|---|---|
| `streamspeech/components/mic-recorder.tsx` | Restored `ttsAudioRef`; grouped all refs together |
| `streamspeech/src/vite-env.d.ts` | **New** — Vite + SpeechRecognition type declarations |
| `streamspeech/tsconfig.json` | Include `src/vite-env.d.ts` |

---

## Frontend Audit — Similar Issues

Scanned all `.tsx`/`.ts` files for `Ref.current` usage without matching `useRef` declarations:

| File | Refs | Status |
|---|---|---|
| `components/mic-recorder.tsx` | 7 refs | ✅ All declared |
| `components/particle-background.tsx` | `canvasRef` | ✅ OK |
| `src/hooks/useAudioWaveform.ts` | 4 refs | ✅ OK |
| `src/hooks/useSpeechRecognition.ts` | 2 refs | ✅ OK |
| `components/ui/calendar.tsx` | `ref` | ✅ OK |

**No other undefined ref issues found.**

---

## Validation Results

| Check | Result |
|---|---|
| `npm run build` | ✅ Pass (3.9s) |
| `npx tsc --noEmit` | ✅ Pass (0 errors) |
| Linter (`mic-recorder.tsx`) | ✅ No errors |
| `ttsAudioRef` declared before use | ✅ Line 45, used at 85 and 332 |
| React hooks import | ✅ `useState, useRef, useCallback, useEffect` from `"react"` |

---

## Prevention

- Keep all `useRef` declarations in one contiguous block at the top of the component.
- Never interleave `useState` and `useRef` hooks when adding new state during refactors.
- Run `npm run build` after any mic-recorder changes.
