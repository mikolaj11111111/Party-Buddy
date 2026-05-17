import { API_BASE_URL } from './config'
import type { FiveSecondsPrompt } from '../types/fiveSeconds'

/** Fetch the authored prompt bank for the 5 Seconds game. */
export async function fetchFiveSecondsPrompts() {
  const response = await fetch(`${API_BASE_URL}/api/5-seconds/prompts`)
  if (!response.ok) {
    throw new Error('Nie udało się pobrać promptów gry 5 sekund.')
  }

  return (await response.json()) as FiveSecondsPrompt[]
}
