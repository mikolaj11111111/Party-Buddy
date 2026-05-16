import { API_BASE_URL } from './config'
import type { HistorySession } from '../types/history'

/** Fetch recent finished game sessions from the backend history API. */
export async function fetchSessionHistory(): Promise<HistorySession[]> {
  const response = await fetch(`${API_BASE_URL}/api/history/sessions`)
  if (!response.ok) {
    throw new Error('Nie udało się pobrać historii sesji.')
  }

  return (await response.json()) as HistorySession[]
}
