export type InputMethod = 'click' | 'voice' | 'text' | 'timeout'

export type PlayerPayload = {
  player_id: string
  player_name: string
}

export type QuestionPayload = {
  id: string
  category: string
  difficulty: string
  question: string
  options: Record<'A' | 'B' | 'C' | 'D', string>
}

export type ScorePayload = {
  player_id: string
  player_name: string
  score: number
}

export type StartSessionPayload = {
  type: 'start_session'
  players: string[]
  categories?: string[]
  round_count: number
  round_seconds: number
}

export type SubmitAnswerPayload = {
  type: 'submit_answer'
  question_id: string
  input_method: 'click' | 'voice' | 'text'
  answer_letter?: 'A' | 'B' | 'C' | 'D'
  answer_text?: string
}

export type SessionStartedEvent = {
  type: 'session_started'
  session_id: string
  players: PlayerPayload[]
  round_count: number
  round_seconds: number
  scoreboard: ScorePayload[]
}

export type RoundStartedEvent = {
  type: 'round_started'
  session_id: string
  round_number: number
  active_player: PlayerPayload
  question: QuestionPayload
  deadline_at: string
  scoreboard: ScorePayload[]
  comment_id?: string | null
  comment_key?: string | null
}

export type AnswerResultEvent = {
  type: 'answer_result'
  session_id: string
  round_number: number
  player: PlayerPayload
  question_id: string
  input_method: InputMethod
  submitted_answer: string
  matched_answer?: 'A' | 'B' | 'C' | 'D' | null
  is_correct: boolean
  correct_answer: 'A' | 'B' | 'C' | 'D'
  explanation?: string | null
  score_delta: number
  timed_out: boolean
  scoreboard: ScorePayload[]
  comment_id?: string | null
  comment_key?: string | null
}

export type RoundTransitionEvent = {
  type: 'round_transition'
  phase: 'intro' | 'between_rounds'
  session_id: string
  next_round_number: number
  next_active_player: PlayerPayload
  starts_at: string
  transition_seconds: number
  scoreboard: ScorePayload[]
  comment_id?: string | null
  comment_key?: string | null
}

export type SessionEndingEvent = {
  type: 'session_ending'
  session_id: string
  ends_at: string
  ending_seconds: number
  scoreboard: ScorePayload[]
  winners: ScorePayload[]
  comment_id?: string | null
  comment_key?: string | null
}

export type SessionFinishedEvent = {
  type: 'session_finished'
  session_id: string
  scoreboard: ScorePayload[]
  winners: ScorePayload[]
  comment_id?: string | null
  comment_key?: string | null
}

export type GameErrorEvent = {
  type: 'error'
  code: string
  message: string
}

export type GameServerEvent =
  | SessionStartedEvent
  | RoundStartedEvent
  | AnswerResultEvent
  | RoundTransitionEvent
  | SessionEndingEvent
  | SessionFinishedEvent
  | GameErrorEvent

export type GameSessionConfig = {
  categories?: string[]
  players: string[]
  roundCount: number
  roundSeconds: number
}

export type GameSnapshot = {
  status: 'idle' | 'connecting' | 'connected' | 'finished' | 'error'
  sessionId: string | null
  players: PlayerPayload[]
  roundCount: number
  roundSeconds: number
  currentRound: number
  activePlayer: PlayerPayload | null
  currentQuestion: QuestionPayload | null
  deadlineAt: string | null
  transition: RoundTransitionEvent | null
  ending: SessionEndingEvent | null
  scoreboard: ScorePayload[]
  winners: ScorePayload[]
  lastResult: AnswerResultEvent | null
  error: string | null
}
