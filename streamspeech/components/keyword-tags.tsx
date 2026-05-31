"use client"

interface KeywordTagsProps {
  keywords?: string[]
}

export function KeywordTags({ keywords = [] }: KeywordTagsProps) {
  if (!keywords.length) return null

  return (
    <div className="flex flex-wrap gap-1.5 mt-2">
      {keywords.map((word) => (
        <span
          key={word}
          className="text-xs px-2 py-0.5 rounded-full bg-violet-500/20 border border-violet-300/25"
        >
          #{word}
        </span>
      ))}
    </div>
  )
}
