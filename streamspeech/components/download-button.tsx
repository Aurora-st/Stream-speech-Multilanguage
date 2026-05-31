"use client"

import { Download } from "lucide-react"

interface DownloadButtonProps {
  url?: string | null
  filename: string
  label?: string
}

export function DownloadButton({ url, filename, label = "Download" }: DownloadButtonProps) {
  if (!url) return null

  return (
    <a
      href={url}
      download={filename}
      className="inline-flex items-center gap-1.5 text-xs glass-button px-2.5 py-1.5 rounded-lg hover:scale-105 transition-all"
    >
      <Download className="w-3.5 h-3.5" />
      {label}
    </a>
  )
}
