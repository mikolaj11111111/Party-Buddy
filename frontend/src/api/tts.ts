import { API_BASE_URL } from './config'

/** Build the backend URL for one cached TTS WAV file. */
export function getTtsAudioUrl(key: string) {
  return `${API_BASE_URL}/api/tts?key=${encodeURIComponent(key)}`
}
