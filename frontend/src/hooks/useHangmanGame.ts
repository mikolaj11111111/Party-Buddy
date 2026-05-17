import { useCallback, useState } from 'react'

import { fetchHangmanWords } from '../api/hangman'
import type { GameSessionConfig, PlayerPayload, ScorePayload } from '../types/game'
import type { HangmanSnapshot, HangmanWord } from '../types/hangman'

const MAX_WRONG_GUESSES = 6

const initialHangmanSnapshot: HangmanSnapshot = {
  status: 'idle',
  sessionConfig: null,
  players: [],
  words: [],
  roundCount: 10,
  currentRound: 0,
  activePlayer: null,
  currentWord: null,
  guessedLetters: [],
  wrongLetters: [],
  maxWrongGuesses: MAX_WRONG_GUESSES,
  scoreboard: [],
  winners: [],
  result: null,
  error: null,
}

/** Manage a local Hangman game session in the browser. */
export function useHangmanGame() {
  const [snapshot, setSnapshot] = useState<HangmanSnapshot>(initialHangmanSnapshot)

  const startSession = useCallback(async (config: GameSessionConfig) => {
    setSnapshot({
      ...initialHangmanSnapshot,
      status: 'loading',
      sessionConfig: config,
      roundCount: config.roundCount,
    })

    try {
      const loadedWords = await fetchHangmanWords()
      const selectedWords = selectWords(loadedWords, config)
      if (selectedWords.length === 0) {
        throw new Error('Brak haseł dla wybranych kategorii.')
      }

      const players = buildPlayers(config.players)
      const scoreboard = buildScoreboard(players)
      setSnapshot({
        ...initialHangmanSnapshot,
        status: 'playing',
        sessionConfig: config,
        players,
        words: selectedWords,
        roundCount: selectedWords.length,
        currentRound: 1,
        activePlayer: players[0] ?? null,
        currentWord: selectedWords[0] ?? null,
        scoreboard,
      })
    } catch (error) {
      setSnapshot((current) => ({
        ...current,
        status: 'error',
        error:
          error instanceof Error
            ? error.message
            : 'Nie udało się uruchomić gry Wisielec.',
      }))
    }
  }, [])

  const guessLetter = useCallback((letter: string) => {
    setSnapshot((current) => {
      if (
        current.status !== 'playing' ||
        !current.currentWord ||
        !current.activePlayer
      ) {
        return current
      }

      const normalizedLetter = letter.toLowerCase()
      if (
        current.guessedLetters.includes(normalizedLetter) ||
        current.wrongLetters.includes(normalizedLetter)
      ) {
        return current
      }

      const word = current.currentWord.word
      if (word.includes(normalizedLetter)) {
        const guessedLetters = [...current.guessedLetters, normalizedLetter]
        if (!isWordSolved(word, guessedLetters)) {
          return {
            ...current,
            guessedLetters,
          }
        }

        const scoreboard = sortScoreboard(
          applyScoreDelta(current.scoreboard, current.activePlayer.player_id, 1),
        )
        return {
          ...current,
          status: 'round_result',
          guessedLetters,
          scoreboard,
          result: {
            solved: true,
            word: current.currentWord,
            scoreDelta: 1,
          },
        }
      }

      const wrongLetters = [...current.wrongLetters, normalizedLetter]
      if (wrongLetters.length < current.maxWrongGuesses) {
        return {
          ...current,
          wrongLetters,
        }
      }

      return {
        ...current,
        status: 'round_result',
        wrongLetters,
        result: {
          solved: false,
          word: current.currentWord,
          scoreDelta: 0,
        },
      }
    })
  }, [])

  const advanceRound = useCallback(() => {
    setSnapshot((current) => {
      if (current.status !== 'round_result') {
        return current
      }

      const nextRound = current.currentRound + 1
      if (nextRound > current.roundCount) {
        const scoreboard = sortScoreboard(current.scoreboard)
        return {
          ...current,
          status: 'finished',
          currentWord: null,
          activePlayer: null,
          guessedLetters: [],
          wrongLetters: [],
          scoreboard,
          winners: getWinners(scoreboard),
        }
      }

      return {
        ...current,
        status: 'playing',
        currentRound: nextRound,
        activePlayer: current.players[(nextRound - 1) % current.players.length] ?? null,
        currentWord: current.words[nextRound - 1] ?? null,
        guessedLetters: [],
        wrongLetters: [],
        result: null,
      }
    })
  }, [])

  const reset = useCallback(() => {
    setSnapshot(initialHangmanSnapshot)
  }, [])

  return {
    advanceRound,
    guessLetter,
    reset,
    snapshot,
    startSession,
  }
}

/** Choose a random word queue matching the setup filters. */
function selectWords(words: HangmanWord[], config: GameSessionConfig): HangmanWord[] {
  const categories = new Set(config.categories ?? [])
  const filteredWords =
    categories.size > 0 ? words.filter((word) => categories.has(word.category)) : words

  return shuffle(filteredWords).slice(0, config.roundCount)
}

/** Convert player names into stable local player payloads. */
function buildPlayers(playerNames: string[]): PlayerPayload[] {
  return playerNames.map((playerName, index) => ({
    player_id: `hangman_player_${index + 1}`,
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

/** Add a solved word point to the active player's score. */
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

/** Check whether every non-space letter in the word has been guessed. */
function isWordSolved(word: string, guessedLetters: string[]) {
  const guessed = new Set(guessedLetters)
  return [...word].every((letter) => letter === ' ' || guessed.has(letter))
}

/** Shuffle without mutating the loaded word list. */
function shuffle<T>(items: T[]) {
  return [...items].sort(() => Math.random() - 0.5)
}
