export type ProcessingStep =
  | "idle"
  | "recording"
  | "uploading"
  | "transcribing"
  | "translating"
  | "synthesizing"
  | "complete"

export interface LatencyBreakdown {
  asr: number
  translation: number
  tts: number
  total: number
}

export interface TranslationResult {
  source_text: string
  translated_text: string
  audio_url: string
  detected_language: string
  confidence?: number | null
  translation_confidence?: number | null
  sentiment?: string
  sentiment_score?: number
  keywords?: string[]
  summary?: string
  audio_duration_ms?: number | null
  cached?: boolean
  latency?: LatencyBreakdown
}

export interface AnalyticsStats {
  total_translations: number
  average_latency_ms: number
  average_audio_duration_ms: number
  average_latency_breakdown: LatencyBreakdown
  cached_responses: number
  success_rate_percent: number
  total_requests: number
  failed_requests: number
  most_used_language: string | null
  languages_used: Array<{ lang: string; count: number }>
  detected_languages: Array<{ lang: string; count: number }>
  sentiment_distribution: Array<{ sentiment: string; count: number }>
  cache_stats: {
    entries: number
    hits: number
    misses: number
    hit_rate_percent: number
  }
}

export interface HistoryEntry extends TranslationResult {
  id: string
  created_at: string
  source_lang?: string | null
  target_lang: string
  cached: boolean
}

export type LanguageCode = "" | "en" | "hi" | "ja" | "es" | "ta"

export const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "hi", label: "Hindi" },
  { code: "ja", label: "Japanese" },
  { code: "es", label: "Spanish" },
  { code: "ta", label: "Tamil" },
] as const

export const SUPPORTED_PAIRS = new Set([
  "ja->en",
  "en->hi",
  "hi->en",
  "en->es",
  "es->en",
  "ta->hi",
  "hi->ta",
])

export const DETECTED_LABELS: Record<string, string> = {
  en: "English",
  hi: "Hindi",
  ja: "Japanese",
  es: "Spanish",
  ta: "Tamil",
}

export const TIMELINE_STEPS = [
  { id: "recording", label: "Recording", icon: "🎤" },
  { id: "uploading", label: "Uploading", icon: "📤" },
  { id: "transcribing", label: "Transcribing", icon: "🧠" },
  { id: "translating", label: "Translating", icon: "🌐" },
  { id: "synthesizing", label: "Synthesizing", icon: "🔊" },
  { id: "complete", label: "Complete", icon: "✅" },
] as const

export function formatDuration(ms: number | null | undefined): string {
  if (!ms || ms <= 0) return "0:00"
  const totalSeconds = Math.round(ms / 1000)
  const minutes = Math.floor(totalSeconds / 60)
  const seconds = totalSeconds % 60
  return `${minutes}:${seconds.toString().padStart(2, "0")}`
}
