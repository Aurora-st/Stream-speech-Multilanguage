"use client"

import { useEffect, useState } from "react"

interface WaveAnimationProps {
  isActive: boolean
}

export function WaveAnimation({ isActive }: WaveAnimationProps) {
  const [bars] = useState(() => Array.from({ length: 5 }, (_, i) => i))

  if (!isActive) return null

  return (
    <div className="flex items-center justify-center gap-1 h-12">
      {bars.map((i) => (
        <div
          key={i}
          className="w-1.5 bg-gradient-to-t from-blue-500 to-purple-500 rounded-full animate-wave"
          style={{
            animationDelay: `${i * 0.1}s`,
            height: "100%",
          }}
        />
      ))}
    </div>
  )
}
