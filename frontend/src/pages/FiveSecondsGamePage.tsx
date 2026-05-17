import { useCountdown } from '../hooks/useCountdown'
import type { FiveSecondsSnapshot } from '../types/fiveSeconds'

type FiveSecondsGamePageProps = {
  game: FiveSecondsSnapshot
  onLeave: () => void
  onScoreRound: (scoreDelta: 0 | 1) => void
}

/** Local game screen for manually judged 5 Seconds rounds. */
export function FiveSecondsGamePage({
  game,
  onLeave,
  onScoreRound,
}: FiveSecondsGamePageProps) {
  const secondsLeft = useCountdown(game.deadlineAt)
  const timerRatio = game.roundSeconds > 0 ? secondsLeft / game.roundSeconds : 0
  const timerPercent = Math.max(0, Math.min(100, timerRatio * 100))
  const canJudge = game.status === 'playing' && game.currentPrompt !== null
  const showExamples = canJudge && secondsLeft === 0

  return (
    <section className="game-layout">
      <header className="game-topbar">
        <div>
          <p className="eyebrow">Runda {game.currentRound || '-'}</p>
          <h1>{game.activePlayer?.player_name ?? 'Ładowanie'}</h1>
        </div>
        <button type="button" className="ghost-button" onClick={onLeave}>
          Menu
        </button>
      </header>

      <div className="game-grid">
        <section className="question-panel five-seconds-panel" aria-live="polite">
          <div className="timer-row">
            <span>{secondsLeft}s</span>
            <div className="timer-track" aria-hidden="true">
              <span style={{ width: `${timerPercent}%` }} />
            </div>
          </div>

          {game.currentPrompt ? (
            <>
              <p className="question-meta">
                {game.currentPrompt.category} / {game.currentPrompt.difficulty}
              </p>
              <h2>{game.currentPrompt.prompt}</h2>

              <div className="judge-actions">
                <button
                  type="button"
                  className="primary-button"
                  disabled={!canJudge}
                  onClick={() => onScoreRound(1)}
                >
                  Zaliczone
                </button>
                <button
                  type="button"
                  className="secondary-button"
                  disabled={!canJudge}
                  onClick={() => onScoreRound(0)}
                >
                  Pudło
                </button>
              </div>
            </>
          ) : (
            <div className="empty-state">
              {game.status === 'loading'
                ? 'Ładowanie gry...'
                : game.error || 'Czekam na rundę'}
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

          {showExamples && game.currentPrompt ? (
            <section className="voice-panel">
              <h2>Przykłady</h2>
              <div className="prompt-examples">
                {game.currentPrompt.sample_answers.map((answer) => (
                  <span key={answer}>{answer}</span>
                ))}
              </div>
            </section>
          ) : null}

          <p className="small-status" aria-live="polite">
            {game.error ?? ''}
          </p>
        </aside>
      </div>
    </section>
  )
}
