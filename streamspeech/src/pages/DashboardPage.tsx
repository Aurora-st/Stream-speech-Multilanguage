"use client"

import { useEffect, useState } from "react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { fetchAnalyticsStats, fetchTranslationHistory } from "@/src/services/api"
import type { AnalyticsStats, HistoryEntry } from "@/src/types/translation"
import { DETECTED_LABELS, formatDuration } from "@/src/types/translation"

const SENTIMENT_COLORS: Record<string, string> = {
  positive: "#34d399",
  neutral: "#94a3b8",
  negative: "#fb7185",
}

export function DashboardPage() {
  const [stats, setStats] = useState<AnalyticsStats | null>(null)
  const [history, setHistory] = useState<HistoryEntry[]>([])
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    void (async () => {
      try {
        const [statsData, historyData] = await Promise.all([
          fetchAnalyticsStats(),
          fetchTranslationHistory(15),
        ])
        setStats(statsData)
        setHistory(historyData)
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load analytics")
      } finally {
        setLoading(false)
      }
    })()
  }, [])

  if (loading) {
    return (
      <div className="glass-card p-8 text-center animate-pulse">
        Loading analytics dashboard...
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass-card p-6 border border-amber-300/30 text-amber-100">
        {error}. Make sure the backend is running on port 8000.
      </div>
    )
  }

  const latencyData = stats
    ? [
        { stage: "ASR", ms: stats.average_latency_breakdown.asr },
        { stage: "Translation", ms: stats.average_latency_breakdown.translation },
        { stage: "TTS", ms: stats.average_latency_breakdown.tts },
      ]
    : []

  const mostUsedLabel = stats?.most_used_language
    ? DETECTED_LABELS[stats.most_used_language] ?? stats.most_used_language
    : "N/A"

  return (
    <div className="space-y-6 w-full">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[
          { label: "Total Translations", value: stats?.total_translations ?? 0, icon: "📊" },
          { label: "Success Rate", value: `${stats?.success_rate_percent ?? 100}%`, icon: "✅" },
          { label: "Avg Latency", value: `${stats?.average_latency_ms ?? 0} ms`, icon: "⚡" },
          { label: "Most Used Language", value: mostUsedLabel, icon: "🌍" },
        ].map((card) => (
          <div key={card.label} className="glass-card p-4">
            <p className="text-xs opacity-60 mb-1">{card.icon} {card.label}</p>
            <p className="text-2xl font-bold">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        {[
          { label: "Cached Responses", value: stats?.cached_responses ?? 0, icon: "💾" },
          { label: "Cache Hit Rate", value: `${stats?.cache_stats.hit_rate_percent ?? 0}%`, icon: "🎯" },
          {
            label: "Avg Audio Duration",
            value: formatDuration(stats?.average_audio_duration_ms),
            icon: "🎧",
          },
        ].map((card) => (
          <div key={card.label} className="glass-card p-4">
            <p className="text-xs opacity-60 mb-1">{card.icon} {card.label}</p>
            <p className="text-xl font-bold">{card.value}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass-card p-4">
          <h3 className="text-sm font-medium mb-4 opacity-80">Average Latency by Stage</h3>
          <div className="h-56">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={latencyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="stage" stroke="rgba(255,255,255,0.5)" fontSize={12} />
                <YAxis stroke="rgba(255,255,255,0.5)" fontSize={12} />
                <Tooltip
                  contentStyle={{
                    background: "rgba(15,23,42,0.9)",
                    border: "1px solid rgba(255,255,255,0.2)",
                    borderRadius: "8px",
                  }}
                />
                <Bar dataKey="ms" fill="#a78bfa" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-4">
          <h3 className="text-sm font-medium mb-4 opacity-80">Sentiment Distribution</h3>
          <div className="h-56">
            {(stats?.sentiment_distribution ?? []).length ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={stats?.sentiment_distribution ?? []}
                    dataKey="count"
                    nameKey="sentiment"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={({ sentiment, count }) => `${sentiment}: ${count}`}
                  >
                    {(stats?.sentiment_distribution ?? []).map((entry) => (
                      <Cell
                        key={entry.sentiment}
                        fill={SENTIMENT_COLORS[entry.sentiment] ?? "#a78bfa"}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <p className="text-sm opacity-50 h-full flex items-center justify-center">
                No sentiment data yet.
              </p>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div className="glass-card p-4">
          <h3 className="text-sm font-medium mb-4 opacity-80">Languages Used (Target)</h3>
          <div className="space-y-2">
            {(stats?.languages_used ?? []).map((item) => (
              <div key={item.lang} className="flex items-center justify-between text-sm">
                <span>{DETECTED_LABELS[item.lang] ?? item.lang}</span>
                <span className="opacity-60">{item.count}</span>
              </div>
            ))}
            {!stats?.languages_used?.length && (
              <p className="text-sm opacity-50">No translations recorded yet.</p>
            )}
          </div>
        </div>

        <div className="glass-card p-4">
          <h3 className="text-sm font-medium mb-4 opacity-80">Detected Source Languages</h3>
          <div className="space-y-2">
            {(stats?.detected_languages ?? []).map((item) => (
              <div key={item.lang} className="flex items-center justify-between text-sm">
                <span>{DETECTED_LABELS[item.lang] ?? item.lang}</span>
                <span className="opacity-60">{item.count}</span>
              </div>
            ))}
            {!stats?.detected_languages?.length && (
              <p className="text-sm opacity-50">No detections recorded yet.</p>
            )}
          </div>
        </div>
      </div>

      <div className="glass-card p-4">
        <h3 className="text-sm font-medium mb-4 opacity-80">Recent Translation History</h3>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {history.map((entry) => (
            <div key={entry.id} className="glass-inactive rounded-xl p-3 text-sm">
              <div className="flex flex-wrap items-center gap-2 mb-1 opacity-60 text-xs">
                <span>{new Date(entry.created_at).toLocaleString()}</span>
                <span>
                  {DETECTED_LABELS[entry.detected_language] ?? entry.detected_language} →{" "}
                  {DETECTED_LABELS[entry.target_lang] ?? entry.target_lang}
                </span>
                {entry.cached && <span className="text-emerald-300">cached</span>}
                {entry.audio_duration_ms && (
                  <span>{formatDuration(entry.audio_duration_ms)}</span>
                )}
              </div>
              <p className="line-clamp-2">{entry.source_text}</p>
              <p className="line-clamp-2 opacity-70 mt-1">{entry.translated_text}</p>
              {entry.latency && (
                <p className="text-xs opacity-50 mt-1">Total: {entry.latency.total} ms</p>
              )}
            </div>
          ))}
          {!history.length && (
            <p className="text-sm opacity-50">No history yet. Record a translation to get started.</p>
          )}
        </div>
      </div>
    </div>
  )
}
