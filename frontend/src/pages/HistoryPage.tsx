import { useCallback, useEffect, useState } from 'react'

import { fetchSessionHistory } from '../api/history'
import type { HistorySession } from '../types/history'

type HistoryPageProps = {
  onBack: () => void
}

type HistoryStatus = 'loading' | 'ready' | 'error'

/** Shows finished local game sessions stored in SQLite. */
export function HistoryPage({ onBack }: HistoryPageProps) {
  const [sessions, setSessions] = useState<HistorySession[]>([])
  const [status, setStatus] = useState<HistoryStatus>('loading')
  const [error, setError] = useState<string | null>(null)

  const applyLoadedHistory = useCallback((loadedSessions: HistorySession[]) => {
    setSessions(loadedSessions)
    setStatus('ready')
  }, [])

  const applyHistoryError = useCallback((loadError: unknown) => {
    setStatus('error')
    setError(
      loadError instanceof Error
        ? loadError.message
        : 'Nie udało się pobrać historii sesji.',
    )
  }, [])

  const loadHistory = useCallback(() => {
    setStatus('loading')
    setError(null)
    fetchSessionHistory().then(applyLoadedHistory).catch(applyHistoryError)
  }, [applyHistoryError, applyLoadedHistory])

  useEffect(() => {
    let isActive = true

    fetchSessionHistory()
      .then((loadedSessions) => {
        if (isActive) {
          applyLoadedHistory(loadedSessions)
        }
      })
      .catch((loadError: unknown) => {
        if (isActive) {
          applyHistoryError(loadError)
        }
      })

    return () => {
      isActive = false
    }
  }, [applyHistoryError, applyLoadedHistory])

  return (
    <section className="history-layout">
      <header className="page-header">
        <button type="button" className="ghost-button" onClick={onBack}>
          Menu
        </button>
        <div>
          <p className="eyebrow">Historia</p>
          <h1>Sesje</h1>
        </div>
      </header>

      {status === 'loading' ? (
        <div className="empty-state">Ładowanie historii...</div>
      ) : null}

      {status === 'error' ? (
        <div className="history-error">
          <p>{error}</p>
          <button type="button" className="secondary-button" onClick={loadHistory}>
            Ponów
          </button>
        </div>
      ) : null}

      {status === 'ready' && sessions.length === 0 ? (
        <div className="empty-state">Brak zapisanych sesji</div>
      ) : null}

      {status === 'ready' && sessions.length > 0 ? (
        <ol className="history-list">
          {sessions.map((session) => (
            <li className="history-card" key={session.id}>
              <div className="history-card__main">
                <div>
                  <p className="eyebrow">{formatMode(session.mode)}</p>
                  <h2>{session.winners.join(', ') || 'Bez zwycięzcy'}</h2>
                </div>
                <strong>{session.top_score}</strong>
              </div>

              <div className="history-card__meta">
                <span>{formatDate(session.finished_at ?? session.created_at)}</span>
                <span>{session.total_rounds} rund</span>
                <span>{session.round_seconds}s</span>
              </div>

              <ol className="history-score-list">
                {session.players.map((player) => (
                  <li key={player.player_id}>
                    <span>{player.player_name}</span>
                    <span>
                      {player.score} / {player.correct_answers}
                    </span>
                  </li>
                ))}
              </ol>
            </li>
          ))}
        </ol>
      ) : null}
    </section>
  )
}

function formatMode(mode: HistorySession['mode']) {
  return mode === 'solo' ? 'Solo' : 'Hotseat'
}

function formatDate(value: string) {
  return new Intl.DateTimeFormat('pl-PL', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}
