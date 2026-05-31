import { useCallback, useRef } from "react"

type BrowserSpeechRecognition = {
  continuous: boolean
  interimResults: boolean
  lang: string
  onresult: ((event: SpeechRecognitionEvent) => void) | null
  onerror: ((event: SpeechRecognitionErrorEvent) => void) | null
  start: () => void
  stop: () => void
}

type SpeechRecognitionConstructor = new () => BrowserSpeechRecognition

type BrowserWindowWithSpeech = Window & {
  SpeechRecognition?: SpeechRecognitionConstructor
  webkitSpeechRecognition?: SpeechRecognitionConstructor
}

export function useSpeechRecognition(
  onTranscript: (text: string, isFinal: boolean) => void,
  onUnsupported?: () => void,
) {
  const recognitionRef = useRef<BrowserSpeechRecognition | null>(null)
  const warnedRef = useRef(false)

  const start = useCallback(
    (lang?: string) => {
      const browserWindow = window as BrowserWindowWithSpeech
      const SpeechRecognition =
        browserWindow.SpeechRecognition || browserWindow.webkitSpeechRecognition

      if (!SpeechRecognition) {
        if (!warnedRef.current) {
          warnedRef.current = true
          onUnsupported?.()
        }
        return
      }

      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      if (lang) recognition.lang = lang

      recognition.onresult = (event: SpeechRecognitionEvent) => {
        let interim = ""
        let finalText = ""
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const chunk = event.results[i][0].transcript
          if (event.results[i].isFinal) {
            finalText += chunk
          } else {
            interim += chunk
          }
        }
        onTranscript((finalText || interim).trim(), Boolean(finalText))
      }

      recognition.onerror = () => {
        onTranscript("", false)
      }

      recognitionRef.current = recognition
      recognition.start()
    },
    [onTranscript, onUnsupported],
  )

  const stop = useCallback(() => {
    recognitionRef.current?.stop()
    recognitionRef.current = null
  }, [])

  return { start, stop }
}
