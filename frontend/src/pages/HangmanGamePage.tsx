import type { HangmanSnapshot } from '../types/hangman'

const HANGMAN_ALPHABET = [
  'a',
  'ą',
  'b',
  'c',
  'ć',
  'd',
  'e',
  'ę',
  'f',
  'g',
  'h',
  'i',
  'j',
  'k',
  'l',
  'ł',
  'm',
  'n',
  'ń',
  'o',
  'ó',
  'p',
  'q',
  'r',
  's',
  'ś',
  't',
  'u',
  'v',
  'w',
  'x',
  'y',
  'z',
  'ź',
  'ż',
] as const

type HangmanGamePageProps = {
  game: HangmanSnapshot
  onAdvanceRound: () => void
  onGuessLetter: (letter: string) => void
  onLeave: () => void
}

/** Local game screen for guessing Hangman words letter by letter. */
export function HangmanGamePage({
  game,
  onAdvanceRound,
  onGuessLetter,
  onLeave,
}: HangmanGamePageProps) {
  const canGuess = game.status === 'playing' && game.currentWord !== null
  const remainingMisses = game.maxWrongGuesses - game.wrongLetters.length
  const revealedWord = game.currentWord
    ? buildRevealedWord(game.currentWord.word, game.guessedLetters)
    : []
  const resultText = game.result?.solved
    ? `Hasło odgadnięte: ${game.result.word.word}`
    : game.result
      ? `Pudło. Hasło: ${game.result.word.word}`
      : null

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
        <section className="question-panel hangman-panel" aria-live="polite">
          {game.currentWord ? (
            <>
              <div className="hangman-progress">
                <span>
                  Błędy: {game.wrongLetters.length} / {game.maxWrongGuesses}
                </span>
                <span>Zostało: {Math.max(0, remainingMisses)}</span>
              </div>

              <p className="question-meta">
                {game.currentWord.category} / {game.currentWord.difficulty}
              </p>
              <h2>{game.currentWord.hint}</h2>

              <div className="hangman-word" aria-label="Ukryte hasło">
                {revealedWord.map((letter, index) => (
                  <span
                    className={`hangman-letter ${
                      letter === ' ' ? 'hangman-letter--space' : ''
                    }`}
                    key={`${letter}-${index}`}
                  >
                    {letter === '_' ? '' : letter.toUpperCase()}
                  </span>
                ))}
              </div>

              {resultText ? (
                <div
                  className={`result-panel ${
                    game.result?.solved ? 'result-panel--ok' : 'result-panel--bad'
                  }`}
                >
                  <h2>{resultText}</h2>
                  <p>{game.result?.scoreDelta ? '+1 punkt' : '0 punktów'}</p>
                  <button
                    type="button"
                    className="primary-button"
                    onClick={onAdvanceRound}
                  >
                    {game.currentRound >= game.roundCount ? 'Wyniki' : 'Następne hasło'}
                  </button>
                </div>
              ) : (
                <div className="hangman-keyboard" aria-label="Wybierz literę">
                  {HANGMAN_ALPHABET.map((letter) => {
                    const isUsed =
                      game.guessedLetters.includes(letter) ||
                      game.wrongLetters.includes(letter)
                    const isWrong = game.wrongLetters.includes(letter)
                    return (
                      <button
                        type="button"
                        className={`hangman-key ${isWrong ? 'hangman-key--wrong' : ''}`}
                        disabled={!canGuess || isUsed}
                        key={letter}
                        onClick={() => onGuessLetter(letter)}
                      >
                        {letter.toUpperCase()}
                      </button>
                    )
                  })}
                </div>
              )}
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

          <section className="voice-panel">
            <h2>Pudła</h2>
            <div className="hangman-misses">
              {Array.from({ length: game.maxWrongGuesses }, (_, index) => (
                <span
                  className={
                    index < game.wrongLetters.length ? 'hangman-miss--active' : ''
                  }
                  key={index}
                >
                  {game.wrongLetters[index]?.toUpperCase() ?? ''}
                </span>
              ))}
            </div>
          </section>

          <p className="small-status" aria-live="polite">
            {game.error ?? ''}
          </p>
        </aside>
      </div>
    </section>
  )
}

/** Build display cells for hidden and revealed letters. */
function buildRevealedWord(word: string, guessedLetters: string[]) {
  const guessed = new Set(guessedLetters)
  return [...word].map((letter) => {
    if (letter === ' ') {
      return ' '
    }

    return guessed.has(letter) ? letter : '_'
  })
}
