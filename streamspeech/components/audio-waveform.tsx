"use client"

interface AudioWaveformProps {
  levels: number[]
  active: boolean
}

export function AudioWaveform({ levels, active }: AudioWaveformProps) {
  if (!active) return null

  return (
    <div className="w-full flex items-end justify-center gap-1 h-16 px-4">
      {levels.slice(0, 32).map((level, index) => (
        <div
          key={index}
          className="w-1.5 rounded-full bg-gradient-to-t from-violet-500 to-fuchsia-300 transition-all duration-75"
          style={{
            height: `${Math.max(8, level * 56)}px`,
            opacity: 0.4 + level * 0.6,
          }}
        />
      ))}
    </div>
  )
}
