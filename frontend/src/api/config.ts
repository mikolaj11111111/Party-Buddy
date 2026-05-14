export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

/** Build the WebSocket URL from Vite env or the configured API URL. */
export function getGameWebSocketUrl() {
  const configuredUrl = import.meta.env.VITE_WS_GAME_URL as string | undefined
  if (configuredUrl) {
    return configuredUrl
  }

  const apiUrl = new URL(API_BASE_URL)
  apiUrl.protocol = apiUrl.protocol === 'https:' ? 'wss:' : 'ws:'
  apiUrl.pathname = '/ws/game'
  apiUrl.search = ''
  return apiUrl.toString()
}
