"use client"

import { useState, useRef, useCallback, useEffect } from "react"
import { Mic } from "lucide-react"
import { AudioWaveform } from "./audio-waveform"
import { DownloadButton } from "./download-button"
import { ProgressTimeline } from "./progress-timeline"
import { ResultCards } from "./result-cards"
import { translateSpeech } from "@/src/services/api"
import { useAudioWaveform } from "@/src/hooks/useAudioWaveform"
import { useSpeechRecognition } from "@/src/hooks/useSpeechRecognition"
import {
  DETECTED_LABELS,
  formatDuration,
  LANGUAGES,
  SUPPORTED_PAIRS,
  type LanguageCode,
  type ProcessingStep,
  type TranslationResult,
} from "@/src/types/translation"

interface MicRecorderProps {
  onError: (message: string) => void
}

export function MicRecorder({ onError }: MicRecorderProps) {
  const [isRecording, setIsRecording] = useState(false)
  const [isProcessing, setIsProcessing] = useState(false)
  const [processingStep, setProcessingStep] = useState<ProcessingStep>("idle")
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null)
  const [recordedObjectUrl, setRecordedObjectUrl] = useState<string | null>(null)
  const [result, setResult] = useState<TranslationResult | null>(null)
  const [liveText, setLiveText] = useState("")
  const [ttsAudioUrl, setTtsAudioUrl] = useState<string | null>(null)
  const [sourceLang, setSourceLang] = useState<LanguageCode>("")
  const [targetLang, setTargetLang] = useState<"en" | "hi" | "ja" | "es" | "ta">("en")
  const [recordingDurationMs, setRecordingDurationMs] = useState(0)

  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const chunksRef = useRef<Blob[]>([])
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const recordedMimeRef = useRef<string>("audio/webm")
  const recordingTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)
  const recordingStartedAtRef = useRef<number | null>(null)
  const ttsAudioRef = useRef<HTMLAudioElement | null>(null)

  const { levels, attachStream, detach } = useAudioWaveform(isRecording)

  const { start: startSpeech, stop: stopSpeech } = useSpeechRecognition(
    (text) => setLiveText(text),
    () => onError("Live speech preview requires Chrome. Final transcription still works via Whisper."),
  )

  const resetAll = useCallback(() => {
    if (mediaRecorderRef.current?.state !== "inactive") {
      mediaRecorderRef.current?.stop()
    }
    stopSpeech()
    detach()
    setIsRecording(false)
    setIsProcessing(false)
    setProcessingStep("idle")
    setAudioBlob(null)
    setResult(null)
    setLiveText("")
    setTtsAudioUrl(null)
    setRecordingDurationMs(0)
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current)
      recordingTimerRef.current = null
    }
  }, [detach, stopSpeech])

  useEffect(() => {
    if (!audioBlob) {
      setRecordedObjectUrl(null)
      return
    }
    const url = URL.createObjectURL(audioBlob)
    setRecordedObjectUrl(url)
    return () => URL.revokeObjectURL(url)
  }, [audioBlob])

  useEffect(() => {
    const el = ttsAudioRef.current
    if (!el || !ttsAudioUrl) return
    el.load()
    void el.play().catch(() => {})
  }, [ttsAudioUrl])

  const stopRecording = useCallback(() => {
    mediaRecorderRef.current?.stop()
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
      timeoutRef.current = null
    }
    if (recordingTimerRef.current) {
      clearInterval(recordingTimerRef.current)
      recordingTimerRef.current = null
    }
    setIsRecording(false)
    stopSpeech()
    detach()
    setProcessingStep("uploading")
  }, [detach, stopSpeech])

  const processAudio = useCallback(
    async (blob: Blob) => {
      setIsProcessing(true)
      try {
        setProcessingStep("uploading")
        await new Promise((r) => setTimeout(r, 120))
        setProcessingStep("transcribing")
        const data = await translateSpeech(blob, targetLang, sourceLang || undefined)
        setResult(data)
        if (data.source_text) setLiveText(data.source_text)
        if (data.audio_url) setTtsAudioUrl(`${data.audio_url}?t=${Date.now()}`)
        setProcessingStep("complete")
      } catch (e) {
        onError(e instanceof Error ? e.message : "Translation failed. Is backend running on port 8000?")
        setProcessingStep("idle")
      } finally {
        setIsProcessing(false)
        setTimeout(() => setProcessingStep("idle"), 1500)
      }
    },
    [onError, sourceLang, targetLang],
  )

  const startRecording = useCallback(async () => {
    try {
      if (sourceLang && sourceLang === targetLang) {
        onError("Source and target languages must be different.")
        return
      }
      if (sourceLang && !SUPPORTED_PAIRS.has(`${sourceLang}->${targetLang}`)) {
        onError("This language pair is not supported yet.")
        return
      }

      resetAll()
      setProcessingStep("recording")

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      attachStream(stream)

      let mimeType = "audio/webm"
      if (!MediaRecorder.isTypeSupported(mimeType)) {
        mimeType = "audio/webm;codecs=opus"
        if (!MediaRecorder.isTypeSupported(mimeType)) mimeType = ""
      }
      recordedMimeRef.current = mimeType || "audio/webm"

      const mediaRecorder = new MediaRecorder(stream, mimeType ? { mimeType } : undefined)
      chunksRef.current = []

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) chunksRef.current.push(event.data)
      }

      mediaRecorder.onstop = () => {
        const blob = new Blob(chunksRef.current, { type: recordedMimeRef.current })
        setAudioBlob(blob)
        stream.getTracks().forEach((t) => t.stop())
        void processAudio(blob)
      }

      mediaRecorderRef.current = mediaRecorder
      startSpeech(sourceLang || undefined)
      mediaRecorder.start()
      setIsRecording(true)
      recordingStartedAtRef.current = Date.now()
      setRecordingDurationMs(0)
      recordingTimerRef.current = setInterval(() => {
        if (recordingStartedAtRef.current) {
          setRecordingDurationMs(Date.now() - recordingStartedAtRef.current)
        }
      }, 200)

      timeoutRef.current = setTimeout(stopRecording, 8000)
    } catch {
      onError("Microphone permission denied. Please allow access.")
    }
  }, [attachStream, onError, processAudio, resetAll, sourceLang, startSpeech, stopRecording, targetLang])

  const toggleRecording = () => {
    if (isRecording) stopRecording()
    else void startRecording()
  }

  useEffect(() => {
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current)
      if (recordingTimerRef.current) clearInterval(recordingTimerRef.current)
      stopSpeech()
      detach()
    }
  }, [detach, stopSpeech])

  const sourceLabel =
    sourceLang === "" ? "Auto detect" : (LANGUAGES.find((l) => l.code === sourceLang)?.label ?? sourceLang)
  const targetLabel = LANGUAGES.find((l) => l.code === targetLang)?.label ?? targetLang
  const detectedLabel = DETECTED_LABELS[result?.detected_language ?? ""] ?? result?.detected_language ?? ""
  const lowConfidence = typeof result?.confidence === "number" && result.confidence < 0.5

  const statusMessage =
    processingStep === "recording"
      ? `Recording... (${sourceLabel})`
      : processingStep === "uploading"
        ? "Uploading audio..."
        : processingStep === "transcribing"
          ? "Transcribing with Whisper..."
          : processingStep === "translating"
            ? "Translating..."
            : processingStep === "synthesizing"
              ? "Synthesizing speech..."
              : processingStep === "complete"
                ? "Complete!"
                : "Tap to start recording"

  const isInvalidCombo = sourceLang !== "" && sourceLang === targetLang
  const isUnsupportedPair = sourceLang !== "" && !SUPPORTED_PAIRS.has(`${sourceLang}->${targetLang}`)
  const displayAudioDurationMs =
    result?.audio_duration_ms ?? (recordingDurationMs > 0 ? recordingDurationMs : null)

  return (
    <div className="flex flex-col items-center gap-6 w-full animate-in fade-in duration-500">
      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-3">
        <label className="flex flex-col gap-1 text-sm opacity-80">
          Source Language (optional)
          <select
            value={sourceLang}
            disabled={isProcessing || isRecording}
            onChange={(e) => setSourceLang(e.target.value as LanguageCode)}
            className="h-10 rounded-xl glass-input px-3 outline-none"
          >
            <option value="" className="text-black">Auto detect</option>
            {LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code} className="text-black">{lang.label}</option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-sm opacity-80">
          Target Language
          <select
            value={targetLang}
            disabled={isProcessing || isRecording}
            onChange={(e) => setTargetLang(e.target.value as typeof targetLang)}
            className="h-10 rounded-xl glass-input px-3 outline-none"
          >
            {LANGUAGES.map((lang) => {
              const disabled =
                (sourceLang !== "" && lang.code === sourceLang) ||
                (sourceLang !== "" && !SUPPORTED_PAIRS.has(`${sourceLang}->${lang.code}`))
              return (
                <option key={lang.code} value={lang.code} disabled={disabled} className="text-black">
                  {lang.label}
                </option>
              )
            })}
          </select>
        </label>
      </div>

      {(isInvalidCombo || isUnsupportedPair) && (
        <div className="w-full rounded-xl border border-amber-300/40 bg-amber-400/15 p-3 text-amber-100 text-sm">
          {isInvalidCombo ? "Source and target must differ." : "Unsupported language pair."}
        </div>
      )}

      <button
        onClick={toggleRecording}
        disabled={isProcessing || isInvalidCombo || isUnsupportedPair}
        className={`relative w-28 h-28 rounded-full flex items-center justify-center transition-all duration-300 ${
          isRecording
            ? "bg-red-500 shadow-[0_0_50px_rgba(239,68,68,0.7)] animate-pulse"
            : "glass-button hover:scale-105"
        } ${isProcessing ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
        aria-label={isRecording ? "Stop recording" : "Start recording"}
      >
        {isRecording && (
          <>
            <span className="absolute -inset-3 rounded-full border border-red-300/50 animate-ping" />
            <span className="absolute inset-0 rounded-full bg-red-500 animate-pulse opacity-30" />
          </>
        )}
        <Mic className={`w-12 h-12 ${isRecording ? "text-white" : "opacity-70"}`} />
      </button>

      <p className="text-sm font-medium opacity-85">{statusMessage}</p>
      {(isRecording || recordingDurationMs > 0) && (
        <p className="text-xs opacity-60">Recording duration: {formatDuration(recordingDurationMs)}</p>
      )}
      <ProgressTimeline step={processingStep} />
      <AudioWaveform levels={levels} active={isRecording} />

      <div className="live-text w-full glass-card p-4 min-h-20">
        <p className="text-sm mb-2 opacity-80">🎤 Live Transcription Preview</p>
        <p className="text-sm leading-relaxed break-words">
          {liveText || (isRecording ? "Listening..." : "Live preview appears while recording (Chrome).")}
        </p>
      </div>

      <ResultCards
        sourceText={result?.source_text ?? ""}
        translatedText={result?.translated_text ?? ""}
        sourceLangLabel={sourceLabel}
        targetLangLabel={targetLabel}
        detectedLanguage={detectedLabel}
        detectedCode={result?.detected_language ?? ""}
        confidence={result?.confidence ?? null}
        translationConfidence={result?.translation_confidence ?? null}
        audioDurationMs={displayAudioDurationMs}
        sentiment={result?.sentiment}
        sentimentScore={result?.sentiment_score}
        keywords={result?.keywords}
        summary={result?.summary}
        cached={result?.cached}
        latency={result?.latency ?? null}
        isProcessing={isProcessing}
        processingStep={processingStep}
        lowConfidence={lowConfidence}
      />

      <div className="w-full glass-card p-4 space-y-4">
        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm opacity-80">🔊 Translated Audio ({targetLabel})</p>
            <DownloadButton url={ttsAudioUrl} filename="translated.mp3" label="Download audio" />
          </div>
          {ttsAudioUrl ? (
            <audio ref={ttsAudioRef} key={ttsAudioUrl} controls src={ttsAudioUrl} className="w-full h-10 rounded-lg" />
          ) : (
            <div className="h-10 rounded-lg glass-inactive flex items-center justify-center text-sm opacity-40">
              Translated speech will appear here
            </div>
          )}
        </div>
        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm opacity-60">Your recording</p>
            {recordedObjectUrl && (
              <DownloadButton url={recordedObjectUrl} filename="recording.webm" label="Download recording" />
            )}
          </div>
          {recordedObjectUrl ? (
            <audio controls src={recordedObjectUrl} className="w-full h-10 rounded-lg" />
          ) : (
            <div className="h-10 rounded-lg glass-inactive flex items-center justify-center text-sm opacity-40">
              Original mic capture
            </div>
          )}
        </div>
        {result?.source_text && (
          <div className="flex gap-2 flex-wrap">
            <DownloadButton
              url={`data:text/plain;charset=utf-8,${encodeURIComponent(result.source_text + "\n\n" + (result.translated_text ?? ""))}`}
              filename="transcript.txt"
              label="Download transcript"
            />
          </div>
        )}
      </div>

      <button onClick={resetAll} className="w-full glass-button py-2 text-sm rounded-xl">
        Reset
      </button>
    </div>
  )
}
