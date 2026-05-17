import Button from '@mui/material/Button'
import ButtonBase from '@mui/material/ButtonBase'

import heroImage from '../assets/hero.png'
import type { GameType } from '../stores/appStore'

type GameOption = {
  game: GameType | 'hangman'
  label: string
  meta: string
  disabled?: boolean
}

const GAME_OPTIONS: GameOption[] = [
  {
    game: 'trivia',
    label: 'Trivia',
    meta: 'dostępne',
  },
  {
    game: 'five_seconds',
    label: '5 sekund',
    meta: 'dostępne',
  },
  {
    game: 'hangman',
    label: 'Wisielec',
    meta: 'później',
    disabled: true,
  },
]

type MenuPageProps = {
  onOpenHistory: () => void
  onSelectGame: (game: GameType) => void
  onSelectMode: (mode: 'solo' | 'hotseat') => void
  selectedGame: GameType
}

/** First app screen for choosing the local trivia mode. */
export function MenuPage({
  onOpenHistory,
  onSelectGame,
  onSelectMode,
  selectedGame,
}: MenuPageProps) {
  return (
    <section className="menu-layout">
      <div className="menu-copy">
        <p className="eyebrow">Party Buddy</p>
        <h1>Wybór gry</h1>

        <section className="menu-section" aria-labelledby="game-choice-title">
          <h2 id="game-choice-title">Gra</h2>
          <div className="game-choice-grid" aria-label="Wybierz grę">
            {GAME_OPTIONS.map((option) => (
              <ButtonBase
                type="button"
                className={`game-choice-button ${
                  option.game === selectedGame ? 'game-choice-button--active' : ''
                }`}
                disabled={option.disabled}
                key={option.game}
                onClick={() => {
                  if (option.game !== 'hangman') {
                    onSelectGame(option.game)
                  }
                }}
              >
                <span className="mode-button__title">{option.label}</span>
                <span className="mode-button__meta">{option.meta}</span>
              </ButtonBase>
            ))}
          </div>
        </section>

        <section className="menu-section" aria-labelledby="mode-choice-title">
          <h2 id="mode-choice-title">Tryb</h2>
          <div className="mode-grid" aria-label="Wybierz tryb gry">
            <ButtonBase
              type="button"
              className="mode-button"
              onClick={() => onSelectMode('solo')}
            >
              <span className="mode-button__title">Solo</span>
              <span className="mode-button__meta">1 gracz</span>
            </ButtonBase>
            <ButtonBase
              type="button"
              className="mode-button mode-button--accent"
              onClick={() => onSelectMode('hotseat')}
            >
              <span className="mode-button__title">Hotseat</span>
              <span className="mode-button__meta">2-6 graczy</span>
            </ButtonBase>
          </div>
        </section>
        <Button
          type="button"
          className="secondary-button"
          onClick={onOpenHistory}
          variant="outlined"
        >
          Historia
        </Button>
      </div>
      <div className="menu-visual" aria-hidden="true">
        <img src={heroImage} alt="" />
      </div>
    </section>
  )
}
