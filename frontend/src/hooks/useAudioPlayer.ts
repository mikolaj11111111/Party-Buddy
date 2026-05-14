import { useCallback, useRef, useState } from 'react'

import { getTtsAudioUrl } from '../api/tts'

/** Play cached TTS audio by key and expose simple playback state. */
export function useAudioPlayer() {
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Stop the active audio element and clear playback state.
  const stop = useCallback(() => {
    audioRef.current?.pause()
    audioRef.current = null
    setIsPlaying(false)
  }, [])

  const playKey = useCallback(
    async (key: string) => {
      // Play one cached TTS WAV file from the backend.
      stop()
      setError(null)
      setIsPlaying(true)

      const audio = new Audio(getTtsAudioUrl(key))
      audioRef.current = audio

      try {
        await new Promise<void>((resolve, reject) => {
          audio.onended = () => resolve()
          audio.onerror = () => reject(new Error('Nie udało się odtworzyć audio.'))
          audio.play().catch(reject)
        })
      } catch (playbackError) {
        setError(
          playbackError instanceof Error
            ? playbackError.message
            : 'Nie udało się odtworzyć audio.',
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
      // Play cached TTS files sequentially in the provided order.
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
