import { useCallback, useRef, useState } from 'react'

import { getTtsAudioUrl } from '../api/tts'

export function useAudioPlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const stop = useCallback(() => {
    audioRef.current?.pause()
    audioRef.current = null
    setIsPlaying(false)
  }, [])

  const playKey = useCallback(
    async (key: string) => {
      stop()
      setError(null)
      setIsPlaying(true)

      const audio = new Audio(getTtsAudioUrl(key))
      audioRef.current = audio

      try {
        await new Promise<void>((resolve, reject) => {
          audio.onended = () => resolve()
          audio.onerror = () => reject(new Error('Nie udalo sie odtworzyc audio.'))
          audio.play().catch(reject)
        })
      } catch (playbackError) {
        setError(
          playbackError instanceof Error
            ? playbackError.message
            : 'Nie udalo sie odtworzyc audio.',
        )
      } finally {
        if (audioRef.current === audio) {
          audioRef.current = null
        }
        setIsPlaying(false)
      }
    },
    [stop],
  )

  const playQueue = useCallback(
    async (keys: string[]) => {
      for (const key of keys) {
        await playKey(key)
      }
    },
    [playKey],
  )

  return {
    error,
    isPlaying,
    playKey,
    playQueue,
    stop,
  }
}
