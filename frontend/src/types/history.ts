export type HistoryScore = {
  player_id: string
  player_name: string
  player_order: number
  score: number
  correct_answers: number
  answered_questions: number
}

export type HistorySession = {
  id: string
  mode: 'solo' | 'hotseat'
  total_rounds: number
  round_seconds: number
  created_at: string
  finished_at: string | null
  top_score: number
  winners: string[]
  players: HistoryScore[]
}
