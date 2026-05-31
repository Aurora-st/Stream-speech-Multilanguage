import { useCallback, useEffect, useRef, useState } from "react"

export function useAudioWaveform(active: boolean) {
  const canvasRef = useRef<HTMLCanvasElement | null>(null)
  const analyserRef = useRef<AnalyserNode | null>(null)
  const animationRef = useRef<number | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const [levels, setLevels] = useState<number[]>(Array(32).fill(0))

  const attachStream = useCallback((stream: MediaStream) => {
    streamRef.current = stream
    const audioContext = new AudioContext()
    const source = audioContext.createMediaStreamSource(stream)
    const analyser = audioContext.createAnalyser()
    analyser.fftSize = 64
    source.connect(analyser)
    analyserRef.current = analyser
  }, [])

  useEffect(() => {
    if (!active || !analyserRef.current) {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
      setLevels(Array(32).fill(0))
      return
    }

    const analyser = analyserRef.current
    const buffer = new Uint8Array(analyser.frequencyBinCount)

    const draw = () => {
      analyser.getByteFrequencyData(buffer)
      const next = Array.from(buffer).map((v) => v / 255)
      setLevels(next)
      animationRef.current = requestAnimationFrame(draw)
    }

    draw()
    return () => {
      if (animationRef.current) cancelAnimationFrame(animationRef.current)
    }
  }, [active])

  const detach = useCallback(() => {
    streamRef.current?.getTracks().forEach((t) => t.stop())
    streamRef.current = null
    analyserRef.current = null
  }, [])

  return { canvasRef, levels, attachStream, detach }
}
