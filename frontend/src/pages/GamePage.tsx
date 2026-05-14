import { useState } from 'react'

import { MicButton } from '../components/MicButton'
import { useCountdown } from '../hooks/useCountdown'
import type { GameSnapshot, SubmitAnswerPayload } from '../types/game'

const ANSWER_LETTERS = ['A', 'B', 'C', 'D'] as const

type GamePageProps = {
  audioError: string | null
  game: GameSnapshot
  isAudioPlaying: boolean
  onLeave: () => void
  onSubmitAnswer: (answer: Omit<SubmitAnswerPayload, 'type'>) => void
}

/** Main live game screen driven by backend WebSocket events. */
export function GamePage({
  audioError,
  game,
  isAudioPlaying,
  onLeave,
  onSubmitAnswer,
}: GamePageProps) {
  const [lastTranscript, setLastTranscript] = useState('')
  const secondsLeft = useCountdown(game.deadlineAt)
  const transitionSecondsLeft = useCountdown(game.transition?.starts_at ?? null)
  const endingSecondsLeft = useCountdown(game.ending?.ends_at ?? null)
  const question = game.currentQuestion
  const isInTransition = !question && game.transition !== null
  const isEnding = !question && game.ending !== null
  const timerRatio = game.roundSeconds > 0 ? secondsLeft / game.roundSeconds : 0
  const transitionRatio =
    game.transition && game.transition.transition_seconds > 0
      ? transitionSecondsLeft / game.transition.transition_seconds
      : 0
  const endingRatio =
    game.ending && game.ending.ending_seconds > 0
      ? endingSecondsLeft / game.ending.ending_seconds
      : 0
  const timerPercent = Math.max(0, Math.min(100, timerRatio * 100))
  const transitionPercent = Math.max(0, Math.min(100, transitionRatio * 100))
  const endingPercent = Math.max(0, Math.min(100, endingRatio * 100))
  const canAnswer = game.status === 'connected' && question !== null && secondsLeft > 0
  const displayedSeconds = isEnding
    ? endingSecondsLeft
    : isInTransition
      ? transitionSecondsLeft
      : secondsLeft
  const displayedPercent = isEnding
    ? endingPercent
    : isInTransition
      ? transitionPercent
      : timerPercent

  const submitLetter = (answerLetter: (typeof ANSWER_LETTERS)[number]) => {
    if (!question || !canAnswer) {
      return
    }

    onSubmitAnswer({
      question_id: question.id,
      input_method: 'click',
      answer_letter: answerLetter,
    })
  }

  const submitVoiceText = (text: string) => {
    setLastTranscript(text)
    if (!question || !canAnswer) {
      return
    }

    onSubmitAnswer({
      question_id: question.id,
      input_method: 'voice',
      answer_text: text,
    })
  }

  return (
    <section className="game-layout">
      <header className="game-topbar">
        <div>
          <p className="eyebrow">Runda {game.currentRound || '-'}</p>
          <h1>{game.activePlayer?.player_name ?? 'Łączenie'}</h1>
        </div>
        <button type="button" className="ghost-button" onClick={onLeave}>
          Menu
        </button>
      </header>

      <div className="game-grid">
        <section className="question-panel" aria-live="polite">
          <div className="timer-row">
            <span>{displayedSeconds}s</span>
            <div className="timer-track" aria-hidden="true">
              <span style={{ width: `${displayedPercent}%` }} />
            </div>
          </div>

          {question ? (
            <>
              <p className="question-meta">
                {question.category} / {question.difficulty}
              </p>
              <h2>{question.question}</h2>
              <div className="answer-grid">
                {ANSWER_LETTERS.map((letter) => (
                  <button
                    type="button"
                    className="answer-button"
                    disabled={!canAnswer}
                    key={letter}
                    onClick={() => submitLetter(letter)}
                  >
                    <span className="answer-letter">{letter}</span>
                    <span>{question.options[letter]}</span>
                  </button>
                ))}
              </div>
            </>
          ) : isEnding ? (
            <div className="transition-state">
              <p className="eyebrow">Koniec gry</p>
              <h2>Wyniki za moment</h2>
              <p>{game.winners.map((winner) => winner.player_name).join(', ')}</p>
            </div>
          ) : isInTransition ? (
            <div className="transition-state">
              <p className="eyebrow">
                {game.transition?.phase === 'intro' ? 'Start gry' : 'Następna runda'}
              </p>
              <h2>Runda {game.transition?.next_round_number}</h2>
              <p>{game.transition?.next_active_player.player_name}</p>
            </div>
          ) : (
            <div className="empty-state">
              {game.status === 'connecting' ? 'Łączenie z grą...' : 'Czekam na rundę'}
            </div>
          )}
        </section>

        <aside className="side-panel">
          <section className="scoreboard-panel">
            <h2>Wynik</h2>
            <ol className="score-list">
              {game.scoreboard.map((score) => (
                <li key={score.player_id}>
                  <span>{score.player_name}</span>
                  <strong>{score.score}</strong>
                </li>
              ))}
            </ol>
          </section>

          <section className="voice-panel">
            <h2>Głos</h2>
            <MicButton disabled={!canAnswer} onTranscript={submitVoiceText} />
            <p className="small-status">{lastTranscript || audioError}</p>
          </section>

          {game.lastResult ? (
            <section
              className={`result-panel ${
                game.lastResult.is_correct ? 'result-panel--ok' : 'result-panel--bad'
              }`}
            >
              <h2>{game.lastResult.is_correct ? 'Poprawnie' : 'Błędnie'}</h2>
              <p>
                {game.lastResult.player.player_name}: {game.lastResult.submitted_answer}
              </p>
              <p>Poprawna: {game.lastResult.correct_answer}</p>
            </section>
          ) : null}

          <p className="small-status" aria-live="polite">
            {game.error ?? (isAudioPlaying ? 'Prowadzący mówi...' : '')}
          </p>
        </aside>
      </div>
    </section>
  )
}
