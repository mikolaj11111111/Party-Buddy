import { API_BASE_URL } from './config'
import type { HangmanWord } from '../types/hangman'

/** Fetch the authored word bank for the Hangman game. */
export async function fetchHangmanWords() {
  const response = await fetch(`${API_BASE_URL}/api/hangman/words`)
  if (!response.ok) {
    throw new Error('Nie udało się pobrać haseł wisielca.')
  }

  return (await response.json()) as HangmanWord[]
}
