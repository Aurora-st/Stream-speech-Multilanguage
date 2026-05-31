"use client"

import { useState, useEffect } from "react"
import { MicRecorder } from "@/components/mic-recorder"

export default function Home() {
  const [toast, setToast] = useState<string | null>(null)
  const [isVisible, setIsVisible] = useState(false)

  useEffect(() => {
    // Trigger fade-in animation on mount
    setIsVisible(true)
  }, [])

  const handleError = (message: string) => {
    setToast(message)
    setTimeout(() => setToast(null), 4000)
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-600 via-purple-600 to-purple-800 flex flex-col items-center justify-center px-4 py-8">
      {/* Toast Notification */}
      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 animate-in fade-in slide-in-from-top-4 duration-300">
          <div className="bg-red-500/90 backdrop-blur-sm text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-3">
            <svg
              className="w-5 h-5 flex-shrink-0"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <span className="text-sm font-medium">{toast}</span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div
        className={`w-full max-w-md transition-all duration-700 ${
          isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
        }`}
      >
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-2 flex items-center justify-center gap-2">
            <span className="text-4xl">🎙️</span>
            <span className="text-balance">Mini StreamSpeech</span>
          </h1>
          <p className="text-white/70 text-sm md:text-base">
            Speak Japanese → Hear English instantly
          </p>
        </header>

        {/* Glassmorphism Card */}
        <div className="bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 shadow-2xl p-6 md:p-8">
          <MicRecorder onError={handleError} />
        </div>

        {/* Footer */}
        <footer className="mt-8 text-center">
          <p className="text-white/50 text-xs">
            Real-time Speech Translation using StreamSpeech Concept
          </p>
        </footer>
      </div>
    </main>
  )
}
