import { useCallback, useState } from 'react'

import { fetchFiveSecondsPrompts } from '../api/fiveSeconds'
import type { GameSessionConfig, PlayerPayload, ScorePayload } from '../types/game'
import type { FiveSecondsPrompt, FiveSecondsSnapshot } from '../types/fiveSeconds'

const initialFiveSecondsSnapshot: FiveSecondsSnapshot = {
  status: 'idle',
  sessionConfig: null,
  players: [],
  prompts: [],
  roundCount: 10,
  roundSeconds: 5,
  currentRound: 0,
  activePlayer: null,
  currentPrompt: null,
  deadlineAt: null,
  scoreboard: [],
  winners: [],
  error: null,
}

/** Manage a local 5 Seconds game session in the browser. */
export function useFiveSecondsGame() {
  const [snapshot, setSnapshot] = useState<FiveSecondsSnapshot>(
    initialFiveSecondsSnapshot,
  )

  const startSession = useCallback(async (config: GameSessionConfig) => {
    setSnapshot({
      ...initialFiveSecondsSnapshot,
      status: 'loading',
      sessionConfig: config,
      roundCount: config.roundCount,
      roundSeconds: config.roundSeconds,
    })

    try {
      const loadedPrompts = await fetchFiveSecondsPrompts()
      const selectedPrompts = selectPrompts(loadedPrompts, config)
      if (selectedPrompts.length === 0) {
        throw new Error('Brak promptów dla wybranych kategorii.')
      }

      const players = buildPlayers(config.players)
      const scoreboard = buildScoreboard(players)
      setSnapshot({
        status: 'playing',
        sessionConfig: config,
        players,
        prompts: selectedPrompts,
        roundCount: selectedPrompts.length,
        roundSeconds: config.roundSeconds,
        currentRound: 1,
        activePlayer: players[0] ?? null,
        currentPrompt: selectedPrompts[0] ?? null,
        deadlineAt: buildDeadline(config.roundSeconds),
        scoreboard,
        winners: [],
        error: null,
      })
    } catch (error) {
      setSnapshot((current) => ({
        ...current,
        status: 'error',
        error:
          error instanceof Error
            ? error.message
            : 'Nie udało się uruchomić gry 5 sekund.',
      }))
    }
  }, [])

  const scoreRound = useCallback((scoreDelta: 0 | 1) => {
    setSnapshot((current) => {
      if (current.status !== 'playing' || !current.activePlayer) {
        return current
      }

      const nextScoreboard = applyScoreDelta(
        current.scoreboard,
        current.activePlayer.player_id,
        scoreDelta,
      )
      const nextRound = current.currentRound + 1
      if (nextRound > current.roundCount) {
        const sortedScoreboard = sortScoreboard(nextScoreboard)
        return {
          ...current,
          status: 'finished',
          currentPrompt: null,
          deadlineAt: null,
          scoreboard: sortedScoreboard,
          winners: getWinners(sortedScoreboard),
        }
      }

      return {
        ...current,
        currentRound: nextRound,
        activePlayer: current.players[(nextRound - 1) % current.players.length] ?? null,
        currentPrompt: current.prompts[nextRound - 1] ?? null,
        deadlineAt: buildDeadline(current.roundSeconds),
        scoreboard: sortScoreboard(nextScoreboard),
      }
    })
  }, [])

  const reset = useCallback(() => {
    setSnapshot(initialFiveSecondsSnapshot)
  }, [])

  return {
    reset,
    scoreRound,
    snapshot,
    startSession,
  }
}

/** Choose a random prompt queue matching the setup filters. */
function selectPrompts(
  prompts: FiveSecondsPrompt[],
  config: GameSessionConfig,
): FiveSecondsPrompt[] {
  const categories = new Set(config.categories ?? [])
  const filteredPrompts =
    categories.size > 0
      ? prompts.filter((prompt) => categories.has(prompt.category))
      : prompts

  return shuffle(filteredPrompts).slice(0, config.roundCount)
}

/** Convert player names into stable local player payloads. */
function buildPlayers(playerNames: string[]): PlayerPayload[] {
  return playerNames.map((playerName, index) => ({
    player_id: `five_seconds_player_${index + 1}`,
    player_name: playerName,
  }))
}

/** Build the initial score rows for one local session. */
function buildScoreboard(players: PlayerPayload[]): ScorePayload[] {
  return players.map((player) => ({
    ...player,
    score: 0,
  }))
}

/** Add the manual judge result to the active player's score. */
function applyScoreDelta(
  scoreboard: ScorePayload[],
  playerId: string,
  scoreDelta: 0 | 1,
) {
  return scoreboard.map((score) =>
    score.player_id === playerId
      ? { ...score, score: score.score + scoreDelta }
      : score,
  )
}

/** Sort score rows for display while preserving deterministic ties by id. */
function sortScoreboard(scoreboard: ScorePayload[]) {
  return [...scoreboard].sort((left, right) => {
    if (right.score !== left.score) {
      return right.score - left.score
    }

    return left.player_id.localeCompare(right.player_id)
  })
}

/** Return all players tied for first place. */
function getWinners(scoreboard: ScorePayload[]) {
  const topScore = scoreboard[0]?.score ?? 0
  return scoreboard.filter((score) => score.score === topScore)
}

/** Build an ISO deadline for the local round timer. */
function buildDeadline(roundSeconds: number) {
  return new Date(Date.now() + roundSeconds * 1000).toISOString()
}

/** Shuffle without mutating the loaded prompt list. */
function shuffle<T>(items: T[]) {
  return [...items].sort(() => Math.random() - 0.5)
}
