import { useMemo, useState } from 'react'

import type { GameType } from '../stores/appStore'
import type { GameSessionConfig } from '../types/game'

const MAX_PLAYERS = 6
const DEFAULT_ROUND_COUNT = 10
const GAME_SETTINGS: Record<GameType, { label: string; roundSeconds: number }> = {
  trivia: { label: 'Trivia', roundSeconds: 15 },
  five_seconds: { label: '5 sekund', roundSeconds: 5 },
  hangman: { label: 'Wisielec', roundSeconds: 0 },
}
const TRIVIA_CATEGORY_OPTIONS = [
  { id: 'geography', label: 'Geografia' },
  { id: 'history', label: 'Historia' },
  { id: 'popculture', label: 'Popkultura' },
  { id: 'movies', label: 'Filmy' },
  { id: 'music', label: 'Muzyka' },
  { id: 'science', label: 'Nauka' },
  { id: 'internet_games', label: 'Internet i gry' },
  { id: 'sport', label: 'Sport' },
  { id: 'technology', label: 'Technologia' },
  { id: 'language_literature', label: 'Język i literatura' },
  { id: 'general', label: 'Ogólne' },
] as const
const FIVE_SECONDS_CATEGORY_OPTIONS = [
  { id: 'everyday', label: 'Codzienne' },
  { id: 'food', label: 'Jedzenie' },
  { id: 'geography', label: 'Geografia' },
  { id: 'sport', label: 'Sport' },
  { id: 'popculture', label: 'Popkultura' },
  { id: 'internet_games', label: 'Internet i gry' },
  { id: 'technology', label: 'Technologia' },
  { id: 'language', label: 'Język' },
  { id: 'school_work', label: 'Szkoła i praca' },
  { id: 'travel', label: 'Podróże' },
  { id: 'home', label: 'Dom' },
  { id: 'party', label: 'Impreza' },
] as const
const HANGMAN_CATEGORY_OPTIONS = [
  { id: 'names', label: 'Imiona' },
  { id: 'countries', label: 'Państwa' },
  { id: 'cities', label: 'Miasta' },
  { id: 'objects', label: 'Przedmioty' },
  { id: 'animals', label: 'Zwierzęta' },
  { id: 'plants', label: 'Rośliny' },
  { id: 'food', label: 'Jedzenie' },
  { id: 'jobs', label: 'Zawody' },
  { id: 'sports', label: 'Sport' },
  { id: 'nature', label: 'Natura' },
  { id: 'technology', label: 'Technologia' },
  { id: 'popculture', label: 'Popkultura' },
  { id: 'abstract', label: 'Abstrakcyjne' },
] as const

type CategoryOption = {
  id: string
  label: string
}

type SetupMode = 'solo' | 'hotseat'

type SetupPageProps = {
  game: GameType
  mode: SetupMode
  onBack: () => void
  onStart: (config: GameSessionConfig) => void
}

/** Collect local player names before opening a game session. */
export function SetupPage({ game, mode, onBack, onStart }: SetupPageProps) {
  const initialCount = mode === 'solo' ? 1 : 2
  const [playerCount, setPlayerCount] = useState(initialCount)
  const [playerNames, setPlayerNames] = useState(() =>
    Array.from({ length: MAX_PLAYERS }, (_, index) => `Gracz ${index + 1}`),
  )
  const [selectedCategories, setSelectedCategories] = useState<string[]>([])
  const categoryOptions = getCategoryOptions(game)
  const gameSettings = GAME_SETTINGS[game]

  const visibleNames = useMemo(
    () => playerNames.slice(0, playerCount).map((name) => name.trim()),
    [playerCount, playerNames],
  )
  const canStart = visibleNames.every(Boolean) && selectedCategories.length > 0
  const modeTitle = mode === 'solo' ? 'Solo' : 'Hotseat'
  const areAllCategoriesSelected = selectedCategories.length === categoryOptions.length

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

  const toggleCategory = (categoryId: string) => {
    setSelectedCategories((current) =>
      current.includes(categoryId)
        ? current.filter((selectedCategory) => selectedCategory !== categoryId)
        : [...current, categoryId],
    )
  }

  const toggleAllCategories = () => {
    setSelectedCategories(
      areAllCategoriesSelected ? [] : categoryOptions.map((category) => category.id),
    )
  }

  const startGame = () => {
    if (!canStart) {
      return
    }

    onStart({
      categories: selectedCategories,
      players: visibleNames,
      roundCount: DEFAULT_ROUND_COUNT,
      roundSeconds: gameSettings.roundSeconds,
    })
  }

  return (
    <section className="setup-layout">
      <header className="page-header">
        <button type="button" className="ghost-button" onClick={onBack}>
          Wróć
        </button>
        <div>
          <p className="eyebrow">
            {gameSettings.label} / {modeTitle}
          </p>
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

        <section className="category-section" aria-labelledby="category-title">
          <div className="category-row">
            <div>
              <h2 id="category-title">Kategorie</h2>
              <p>
                {selectedCategories.length} z {categoryOptions.length} wybranych
              </p>
            </div>
            <button
              type="button"
              className="secondary-button"
              onClick={toggleAllCategories}
            >
              {areAllCategoriesSelected ? 'Odznacz' : 'Wszystkie'}
            </button>
          </div>

          <div className="category-grid" aria-label="Wybierz kategorie">
            {categoryOptions.map((category) => {
              const isSelected = selectedCategories.includes(category.id)
              return (
                <button
                  type="button"
                  className={`category-button ${
                    isSelected ? 'category-button--active' : ''
                  }`}
                  key={category.id}
                  onClick={() => toggleCategory(category.id)}
                  aria-pressed={isSelected}
                >
                  {category.label}
                </button>
              )
            })}
          </div>
        </section>
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

/** Return category choices for the selected game type. */
function getCategoryOptions(game: GameType): readonly CategoryOption[] {
  if (game === 'trivia') {
    return TRIVIA_CATEGORY_OPTIONS
  }

  if (game === 'five_seconds') {
    return FIVE_SECONDS_CATEGORY_OPTIONS
  }

  return HANGMAN_CATEGORY_OPTIONS
}
