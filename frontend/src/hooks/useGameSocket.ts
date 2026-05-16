import { useCallback, useEffect, useRef, useState } from 'react'

import { getGameWebSocketUrl } from '../api/config'
import type {
  AnswerResultEvent,
  GameServerEvent,
  GameSessionConfig,
  GameSnapshot,
  SubmitAnswerPayload,
} from '../types/game'

const initialGameSnapshot: GameSnapshot = {
  status: 'idle',
  sessionId: null,
  players: [],
  roundCount: 10,
  roundSeconds: 15,
  currentRound: 0,
  activePlayer: null,
  currentQuestion: null,
  deadlineAt: null,
  transition: null,
  ending: null,
  scoreboard: [],
  winners: [],
  lastResult: null,
  error: null,
}

type UseGameSocketOptions = {
  onCommentKey?: (key: string) => void
}

/** Manage the bidirectional game WebSocket and expose UI-ready state. */
export function useGameSocket(options: UseGameSocketOptions = {}) {
  const socketRef = useRef<WebSocket | null>(null)
  const commentHandlerRef = useRef(options.onCommentKey)
  const [snapshot, setSnapshot] = useState<GameSnapshot>(initialGameSnapshot)

  useEffect(() => {
    commentHandlerRef.current = options.onCommentKey
  }, [options.onCommentKey])

  const closeSocket = useCallback(() => {
    socketRef.current?.close()
    socketRef.current = null
  }, [])

  const applyEvent = useCallback((event: GameServerEvent) => {
    if ('comment_key' in event && event.comment_key) {
      commentHandlerRef.current?.(event.comment_key)
    }

    setSnapshot((current) => reduceGameEvent(current, event))
  }, [])

  const startSession = useCallback(
    (config: GameSessionConfig) => {
      closeSocket()
      setSnapshot({
        ...initialGameSnapshot,
        status: 'connecting',
        roundCount: config.roundCount,
        roundSeconds: config.roundSeconds,
      })

      const socket = new WebSocket(getGameWebSocketUrl())
      socketRef.current = socket

      socket.onopen = () => {
        socket.send(
          JSON.stringify({
            type: 'start_session',
            categories: config.categories,
            players: config.players,
            round_count: config.roundCount,
            round_seconds: config.roundSeconds,
          }),
        )
      }

      socket.onmessage = (message) => {
        try {
          applyEvent(JSON.parse(message.data) as GameServerEvent)
        } catch {
          setSnapshot((current) => ({
            ...current,
            status: 'error',
            error: 'Nie udało się odczytać odpowiedzi serwera.',
          }))
        }
      }

      socket.onerror = () => {
        setSnapshot((current) => ({
          ...current,
          status: 'error',
          error: 'Połączenie gry zostało przerwane.',
        }))
      }

      socket.onclose = () => {
        socketRef.current = null
      }
    },
    [applyEvent, closeSocket],
  )

  const submitAnswer = useCallback((answer: Omit<SubmitAnswerPayload, 'type'>) => {
    const socket = socketRef.current
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      setSnapshot((current) => ({
        ...current,
        error: 'Gra nie jest połączona z backendem.',
      }))
      return
    }

    socket.send(JSON.stringify({ type: 'submit_answer', ...answer }))
  }, [])

  const reset = useCallback(() => {
    closeSocket()
    setSnapshot(initialGameSnapshot)
  }, [closeSocket])

  useEffect(() => closeSocket, [closeSocket])

  return {
    reset,
    snapshot,
    startSession,
    submitAnswer,
  }
}

/** Apply one backend event to the frontend game snapshot. */
function reduceGameEvent(current: GameSnapshot, event: GameServerEvent): GameSnapshot {
  switch (event.type) {
    case 'session_started':
      return {
        ...current,
        status: 'connected',
        sessionId: event.session_id,
        players: event.players,
        roundCount: event.round_count,
        roundSeconds: event.round_seconds,
        scoreboard: event.scoreboard,
        error: null,
      }
    case 'round_started':
      return {
        ...current,
        status: 'connected',
        sessionId: event.session_id,
        currentRound: event.round_number,
        activePlayer: event.active_player,
        currentQuestion: event.question,
        deadlineAt: event.deadline_at,
        transition: null,
        ending: null,
        scoreboard: event.scoreboard,
        error: null,
      }
    case 'answer_result':
      return applyAnswerResult(current, event)
    case 'round_transition':
      return {
        ...current,
        status: 'connected',
        sessionId: event.session_id,
        currentRound: event.next_round_number,
        activePlayer: event.next_active_player,
        currentQuestion: null,
        deadlineAt: null,
        transition: event,
        ending: null,
        scoreboard: event.scoreboard,
        error: null,
      }
    case 'session_ending':
      return {
        ...current,
        status: 'connected',
        sessionId: event.session_id,
        currentQuestion: null,
        deadlineAt: null,
        transition: null,
        ending: event,
        scoreboard: event.scoreboard,
        winners: event.winners,
        error: null,
      }
    case 'session_finished':
      return {
        ...current,
        status: 'finished',
        sessionId: event.session_id,
        currentQuestion: null,
        deadlineAt: null,
        transition: null,
        ending: null,
        scoreboard: event.scoreboard,
        winners: event.winners,
        error: null,
      }
    case 'error':
      return {
        ...current,
        status: current.status === 'connecting' ? 'error' : current.status,
        error: event.message,
      }
  }
}

/** Store the latest judged answer while keeping the session live. */
function applyAnswerResult(
  current: GameSnapshot,
  event: AnswerResultEvent,
): GameSnapshot {
  return {
    ...current,
    sessionId: event.session_id,
    currentQuestion: null,
    deadlineAt: null,
    transition: null,
    ending: null,
    scoreboard: event.scoreboard,
    lastResult: event,
    error: null,
  }
}
