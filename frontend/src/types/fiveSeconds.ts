import type { GameSessionConfig, PlayerPayload, ScorePayload } from './game'

export type FiveSecondsPrompt = {
  id: string
  category: string
  difficulty: string
  prompt: string
  expected_answer_count: number
  sample_answers: string[]
}

export type FiveSecondsStatus = 'idle' | 'loading' | 'playing' | 'finished' | 'error'

export type FiveSecondsSnapshot = {
  status: FiveSecondsStatus
  sessionConfig: GameSessionConfig | null
  players: PlayerPayload[]
  prompts: FiveSecondsPrompt[]
  roundCount: number
  roundSeconds: number
  currentRound: number
  activePlayer: PlayerPayload | null
  currentPrompt: FiveSecondsPrompt | null
  deadlineAt: string | null
  scoreboard: ScorePayload[]
  winners: ScorePayload[]
  error: string | null
}
