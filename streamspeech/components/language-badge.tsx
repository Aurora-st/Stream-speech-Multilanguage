"use client"

import { DETECTED_LABELS } from "@/src/types/translation"

interface LanguageBadgeProps {
  code: string
  confidence?: number | null
}

export function LanguageBadge({ code, confidence }: LanguageBadgeProps) {
  const label = DETECTED_LABELS[code] ?? code
  const pct = typeof confidence === "number" ? Math.round(confidence * 100) : null

  return (
    <div className="inline-flex items-center gap-2 flex-wrap">
      <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-sky-500/20 border border-sky-300/30">
        🌐 {label}
      </span>
      {pct !== null && (
        <span className="inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full bg-emerald-500/20 border border-emerald-300/30">
          Confidence {pct}%
          <span
            className="inline-block h-1.5 w-12 rounded-full bg-white/20 overflow-hidden"
            aria-hidden
          >
            <span
              className="block h-full rounded-full bg-emerald-400 transition-all"
              style={{ width: `${pct}%` }}
            />
          </span>
        </span>
      )}
    </div>
  )
}
