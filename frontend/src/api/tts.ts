const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export function getTtsAudioUrl(key: string) {
  return `${API_BASE_URL}/api/tts?key=${encodeURIComponent(key)}`
}
