import { useMemo, useState } from 'react'

import type { GameSessionConfig } from '../types/game'

const MAX_PLAYERS = 6
const DEFAULT_ROUND_COUNT = 10
const DEFAULT_ROUND_SECONDS = 15

type SetupMode = 'solo' | 'hotseat'

type SetupPageProps = {
  mode: SetupMode
  onBack: () => void
  onStart: (config: GameSessionConfig) => void
}

/** Collect local player names before opening a game session. */
export function SetupPage({ mode, onBack, onStart }: SetupPageProps) {
  const initialCount = mode === 'solo' ? 1 : 2
  const [playerCount, setPlayerCount] = useState(initialCount)
  const [playerNames, setPlayerNames] = useState(() =>
    Array.from({ length: MAX_PLAYERS }, (_, index) => `Gracz ${index + 1}`),
  )

  const visibleNames = useMemo(
    () => playerNames.slice(0, playerCount).map((name) => name.trim()),
    [playerCount, playerNames],
  )
  const canStart = visibleNames.every(Boolean)
  const modeTitle = mode === 'solo' ? 'Solo' : 'Hotseat'

  const updatePlayerCount = (nextCount: number) => {
    if (mode === 'solo') {
      setPlayerCount(1)
      return
    }

    setPlayerCount(Math.min(MAX_PLAYERS, Math.max(2, nextCount)))
  }

  const updatePlayerName = (index: number, value: string) => {
    setPlayerNames((current) =>
      current.map((name, nameIndex) => (nameIndex === index ? value : name)),
    )
  }

  const startGame = () => {
    if (!canStart) {
      return
    }

    onStart({
      players: visibleNames,
      roundCount: DEFAULT_ROUND_COUNT,
      roundSeconds: DEFAULT_ROUND_SECONDS,
    })
  }

  return (
    <section className="setup-layout">
      <header className="page-header">
        <button type="button" className="ghost-button" onClick={onBack}>
          Wróć
        </button>
        <div>
          <p className="eyebrow">{modeTitle}</p>
          <h1>Ustaw graczy</h1>
        </div>
      </header>

      <div className="setup-panel">
        <div className="player-count-row">
          <span>Liczba graczy</span>
          <div className="stepper" aria-label="Liczba graczy">
            <button
              type="button"
              className="icon-button"
              disabled={mode === 'solo' || playerCount <= 2}
              onClick={() => updatePlayerCount(playerCount - 1)}
              aria-label="Zmniejsz liczbę graczy"
            >
              -
            </button>
            <output>{playerCount}</output>
            <button
              type="button"
              className="icon-button"
              disabled={mode === 'solo' || playerCount >= MAX_PLAYERS}
              onClick={() => updatePlayerCount(playerCount + 1)}
              aria-label="Zwiększ liczbę graczy"
            >
              +
            </button>
          </div>
        </div>

        <div className="player-form">
          {visibleNames.map((_, index) => (
            <label className="player-field" key={index}>
              <span>Gracz {index + 1}</span>
              <input
                value={playerNames[index]}
                maxLength={32}
                onChange={(event) => updatePlayerName(index, event.target.value)}
              />
            </label>
          ))}
        </div>
      </div>

      <div className="setup-actions">
        <button
          type="button"
          className="primary-button"
          disabled={!canStart}
          onClick={startGame}
        >
          Start
        </button>
      </div>
    </section>
  )
}
