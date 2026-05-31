"use client"

import type { ProcessingStep } from "@/src/types/translation"
import { TIMELINE_STEPS } from "@/src/types/translation"

interface ProgressTimelineProps {
  step: ProcessingStep
}

export function ProgressTimeline({ step }: ProgressTimelineProps) {
  const currentIndex = TIMELINE_STEPS.findIndex((s) => s.id === step)

  return (
    <div className="w-full glass-card p-4">
      <p className="text-sm mb-3 opacity-80">Progress Timeline</p>
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2 text-xs">
        {TIMELINE_STEPS.map((item, idx) => {
          const isActive = step !== "idle" && idx <= currentIndex
          const isCurrent = item.id === step
          return (
            <div
              key={item.id}
              className={`rounded-lg px-2 py-2 border transition-all duration-300 text-center ${
                isCurrent
                  ? "glass-active border-white/50 scale-[1.02]"
                  : isActive
                    ? "glass-active"
                    : "glass-inactive"
              }`}
            >
              <span className="block text-base mb-0.5">{item.icon}</span>
              <span>{item.label}</span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
