"use client"

import { Link, useLocation } from "react-router-dom"
import { BarChart3, Mic } from "lucide-react"
import { ThemeToggle } from "@/components/theme-toggle"
import { ParticleBackground } from "@/components/particle-background"

interface AppLayoutProps {
  children: React.ReactNode
  toast: string | null
}

export function AppLayout({ children, toast }: AppLayoutProps) {
  const location = useLocation()
  const isDashboard = location.pathname === "/dashboard"

  return (
    <main className="min-h-screen app-gradient flex flex-col items-center justify-center px-4 py-10 relative overflow-hidden">
      <ParticleBackground />

      {toast && (
        <div className="fixed top-4 left-1/2 -translate-x-1/2 z-50 animate-in fade-in slide-in-from-top-4 duration-300">
          <div className="bg-red-500/90 backdrop-blur-sm text-white px-6 py-3 rounded-xl shadow-lg flex items-center gap-3">
            <span className="text-sm font-medium">{toast}</span>
          </div>
        </div>
      )}

      <div className="w-full max-w-4xl relative z-10 transition-all duration-700">
        <header className="text-center mb-6">
          <div className="flex items-center justify-between mb-4">
            <nav className="flex gap-2">
              <Link
                to="/"
                className={`glass-button px-3 py-2 rounded-xl text-sm inline-flex items-center gap-1.5 ${
                  !isDashboard ? "glass-active" : ""
                }`}
              >
                <Mic className="w-4 h-4" /> Recorder
              </Link>
              <Link
                to="/dashboard"
                className={`glass-button px-3 py-2 rounded-xl text-sm inline-flex items-center gap-1.5 ${
                  isDashboard ? "glass-active" : ""
                }`}
              >
                <BarChart3 className="w-4 h-4" /> Dashboard
              </Link>
            </nav>
            <ThemeToggle />
          </div>
          <h1 className="text-3xl md:text-5xl font-bold mb-2 flex items-center justify-center gap-2">
            <span className="text-4xl">🎙️</span>
            <span className="text-balance">StreamSpeech</span>
          </h1>
          <p className="opacity-70 text-sm md:text-base">
            Real-time multilingual speech translation with AI analytics
          </p>
        </header>

        <div className="glass-card-main p-6 md:p-8">{children}</div>

        <footer className="mt-8 text-center">
          <p className="opacity-50 text-xs">
            Whisper ASR · Google Translate · gTTS · FastAPI · React
          </p>
        </footer>
      </div>
    </main>
  )
}
