"use client"

import type { LatencyBreakdown, ProcessingStep } from "@/src/types/translation"
import { formatDuration } from "@/src/types/translation"
import { CopyButton } from "./copy-button"
import { KeywordTags } from "./keyword-tags"
import { LanguageBadge } from "./language-badge"
import { SentimentBadge } from "./sentiment-badge"

interface ResultCardsProps {
  sourceText: string
  translatedText: string
  sourceLangLabel: string
  targetLangLabel: string
  detectedLanguage: string
  detectedCode: string
  confidence: number | null
  translationConfidence?: number | null
  audioDurationMs?: number | null
  sentiment?: string
  sentimentScore?: number
  keywords?: string[]
  summary?: string
  cached?: boolean
  latency: LatencyBreakdown | null
  isProcessing: boolean
  processingStep: ProcessingStep
  lowConfidence: boolean
}

export function ResultCards({
  sourceText,
  translatedText,
  sourceLangLabel,
  targetLangLabel,
  detectedLanguage,
  detectedCode,
  confidence,
  translationConfidence,
  audioDurationMs,
  sentiment,
  sentimentScore,
  keywords,
  summary,
  cached,
  latency,
  isProcessing,
  processingStep,
  lowConfidence,
}: ResultCardsProps) {
  const recognitionPlaceholder =
    processingStep === "transcribing"
      ? "Transcribing..."
      : sourceText || `Detected ${sourceLangLabel} text will appear here`
  const translationPlaceholder =
    processingStep === "translating"
      ? "Translating..."
      : translatedText || `Translated ${targetLangLabel} text will appear here`

  return (
    <div className="space-y-4 w-full">
      <div className="glass-card p-4 hover:scale-[1.01] transition-all duration-300">
        <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
          <span className="text-sm font-medium">🧠 Recognized Speech ({sourceLangLabel})</span>
          {sourceText && <CopyButton text={sourceText} label="Copy transcript" />}
        </div>
        <p className="text-lg leading-relaxed">
          {isProcessing && processingStep === "transcribing" ? (
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-sky-300 rounded-full animate-pulse" />
              {recognitionPlaceholder}
            </span>
          ) : (
            recognitionPlaceholder
          )}
        </p>
        {!isProcessing && detectedCode && (
          <div className="mt-3 space-y-2">
            <LanguageBadge code={detectedCode} confidence={confidence} />
            {typeof translationConfidence === "number" && (
              <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-indigo-500/20 border border-indigo-300/30">
                Translation confidence {Math.round(translationConfidence * 100)}%
              </span>
            )}
            {typeof audioDurationMs === "number" && audioDurationMs > 0 && (
              <span className="text-xs opacity-60">Audio duration: {formatDuration(audioDurationMs)}</span>
            )}
            {sentiment && <SentimentBadge sentiment={sentiment} score={sentimentScore} />}
            <KeywordTags keywords={keywords} />
            {summary && (
              <p className="text-xs opacity-70 mt-2">
                <span className="font-medium">Summary:</span> {summary}
              </p>
            )}
            {cached && (
              <p className="text-xs text-emerald-300/80">⚡ Served from cache</p>
            )}
            {lowConfidence && (
              <p className="text-amber-200 text-xs">Low confidence — please speak clearly.</p>
            )}
          </div>
        )}
      </div>

      <div className="glass-card p-4 hover:scale-[1.01] transition-all duration-300">
        <div className="flex items-center justify-between gap-2 mb-2 flex-wrap">
          <span className="text-sm font-medium">🌐 Translated Output ({targetLangLabel})</span>
          {translatedText && <CopyButton text={translatedText} label="Copy translation" />}
        </div>
        <p className="text-lg leading-relaxed">
          {isProcessing && processingStep === "translating" ? (
            <span className="flex items-center gap-2">
              <span className="inline-block w-2 h-2 bg-violet-300 rounded-full animate-pulse" />
              {translationPlaceholder}
            </span>
          ) : (
            translationPlaceholder
          )}
        </p>
      </div>

      {latency && !isProcessing && (
        <div className="glass-card p-4">
          <div className="text-sm font-medium opacity-70 mb-3">Latency Breakdown (ms)</div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: "ASR", value: latency.asr, color: "from-sky-400 to-blue-500" },
              { label: "Translation", value: latency.translation, color: "from-violet-400 to-purple-500" },
              { label: "TTS", value: latency.tts, color: "from-fuchsia-400 to-pink-500" },
              { label: "Total", value: latency.total, color: "from-emerald-400 to-teal-500" },
            ].map((item) => (
              <div key={item.label} className="glass-inactive rounded-xl p-3 text-center">
                <p className="text-xs opacity-60 mb-1">{item.label}</p>
                <p className={`text-xl font-bold bg-gradient-to-r ${item.color} bg-clip-text text-transparent`}>
                  {item.value}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
