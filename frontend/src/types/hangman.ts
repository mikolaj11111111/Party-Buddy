import type { GameSessionConfig, PlayerPayload, ScorePayload } from './game'

export type HangmanWord = {
  id: string
  category: string
  difficulty: string
  word: string
  hint: string
}

export type HangmanStatus =
  | 'idle'
  | 'loading'
  | 'playing'
  | 'round_result'
  | 'finished'
  | 'error'

export type HangmanRoundResult = {
  solved: boolean
  word: HangmanWord
  scoreDelta: 0 | 1
}

export type HangmanSnapshot = {
  status: HangmanStatus
  sessionConfig: GameSessionConfig | null
  players: PlayerPayload[]
  words: HangmanWord[]
  roundCount: number
  currentRound: number
  activePlayer: PlayerPayload | null
  currentWord: HangmanWord | null
  guessedLetters: string[]
  wrongLetters: string[]
  maxWrongGuesses: number
  scoreboard: ScorePayload[]
  winners: ScorePayload[]
  result: HangmanRoundResult | null
  error: string | null
}
