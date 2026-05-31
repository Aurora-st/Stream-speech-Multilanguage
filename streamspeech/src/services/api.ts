import type { AnalyticsStats, HistoryEntry, TranslationResult } from "@/src/types/translation"

const API_BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000"

async function parseError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as {
      detail?: unknown
      error?: string | { message?: string }
    }
    if (typeof body.error === "object" && body.error?.message) return body.error.message
    if (typeof body.error === "string") return body.error
    if (typeof body.detail === "string") return body.detail
    if (Array.isArray(body.detail)) return body.detail.map(String).join(", ")
  } catch {
    /* ignore */
  }
  return res.statusText || "Request failed"
}

export async function translateSpeech(
  audio: Blob,
  targetLang: string,
  sourceLang?: string,
): Promise<TranslationResult> {
  const formData = new FormData()
  formData.append("audio", audio, "input.webm")
  formData.append("target_lang", targetLang)
  if (sourceLang) {
    formData.append("source_lang", sourceLang)
  }

  const res = await fetch(`${API_BASE}/translate-speech`, {
    method: "POST",
    body: formData,
  })

  if (!res.ok) {
    throw new Error(await parseError(res))
  }

  return (await res.json()) as TranslationResult
}

export async function fetchAnalyticsStats(): Promise<AnalyticsStats> {
  const res = await fetch(`${API_BASE}/analytics/stats`)
  if (!res.ok) {
    throw new Error(await parseError(res))
  }
  return (await res.json()) as AnalyticsStats
}

export async function fetchTranslationHistory(limit = 20): Promise<HistoryEntry[]> {
  const res = await fetch(`${API_BASE}/analytics/history?limit=${limit}`)
  if (!res.ok) {
    throw new Error(await parseError(res))
  }
  const data = (await res.json()) as { history: HistoryEntry[] }
  return data.history
}

export async function checkHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/health`)
    return res.ok
  } catch {
    return false
  }
}

export { API_BASE }
