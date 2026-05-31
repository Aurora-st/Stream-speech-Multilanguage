"use client"

import { MicRecorder } from "@/components/mic-recorder"

interface RecorderPageProps {
  onError: (message: string) => void
}

export function RecorderPage({ onError }: RecorderPageProps) {
  return <MicRecorder onError={onError} />
}
