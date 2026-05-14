import heroImage from '../assets/hero.png'

type MenuPageProps = {
  onSelectMode: (mode: 'solo' | 'hotseat') => void
}

/** First app screen for choosing the local trivia mode. */
export function MenuPage({ onSelectMode }: MenuPageProps) {
  return (
    <section className="menu-layout">
      <div className="menu-copy">
        <p className="eyebrow">Party Buddy</p>
        <h1>Trivia ABCD</h1>
        <div className="mode-grid" aria-label="Wybierz tryb gry">
          <button
            type="button"
            className="mode-button"
            onClick={() => onSelectMode('solo')}
          >
            <span className="mode-button__title">Solo</span>
            <span className="mode-button__meta">1 gracz</span>
          </button>
          <button
            type="button"
            className="mode-button mode-button--accent"
            onClick={() => onSelectMode('hotseat')}
          >
            <span className="mode-button__title">Hotseat</span>
            <span className="mode-button__meta">2-6 graczy</span>
          </button>
        </div>
      </div>
      <div className="menu-visual" aria-hidden="true">
        <img src={heroImage} alt="" />
      </div>
    </section>
  )
}
