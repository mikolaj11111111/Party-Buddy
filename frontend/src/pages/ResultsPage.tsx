import type { GameSnapshot } from '../types/game'

type ResultsPageProps = {
  game: GameSnapshot
  onBackToMenu: () => void
  onPlayAgain: () => void
}

/** Final ranking screen after the backend finishes the session. */
export function ResultsPage({ game, onBackToMenu, onPlayAgain }: ResultsPageProps) {
  const winners = game.winners.length > 0 ? game.winners : game.scoreboard.slice(0, 1)
  const winnerNames = winners.map((winner) => winner.player_name).join(', ')

  return (
    <section className="results-layout">
      <header className="page-header">
        <div>
          <p className="eyebrow">Koniec gry</p>
          <h1>{winnerNames || 'Wyniki'}</h1>
        </div>
      </header>

      <ol className="results-list">
        {game.scoreboard.map((score, index) => (
          <li className="result-row" key={score.player_id}>
            <span className="result-rank">{index + 1}</span>
            <span>{score.player_name}</span>
            <strong>{score.score}</strong>
          </li>
        ))}
      </ol>

      <div className="setup-actions">
        <button type="button" className="primary-button" onClick={onPlayAgain}>
          Zagraj ponownie
        </button>
        <button type="button" className="secondary-button" onClick={onBackToMenu}>
          Menu
        </button>
      </div>
    </section>
  )
}
