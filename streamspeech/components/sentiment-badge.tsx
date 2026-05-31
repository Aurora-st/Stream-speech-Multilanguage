"use client"

interface SentimentBadgeProps {
  sentiment?: string
  score?: number
}

const SENTIMENT_STYLE: Record<string, string> = {
  positive: "bg-emerald-500/20 border-emerald-300/30 text-emerald-100",
  negative: "bg-rose-500/20 border-rose-300/30 text-rose-100",
  neutral: "bg-slate-500/20 border-slate-300/30 text-slate-100",
}

export function SentimentBadge({ sentiment = "neutral", score = 0.5 }: SentimentBadgeProps) {
  const style = SENTIMENT_STYLE[sentiment] ?? SENTIMENT_STYLE.neutral
  const emoji = sentiment === "positive" ? "😊" : sentiment === "negative" ? "😔" : "😐"

  return (
    <span className={`inline-flex items-center gap-1 text-xs px-2.5 py-1 rounded-full border ${style}`}>
      {emoji} {sentiment} ({Math.round(score * 100)}%)
    </span>
  )
}
