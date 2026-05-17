import { useCallback } from 'react'
import { AnimatePresence, motion } from 'motion/react'

import './App.css'
import { useGameSocket } from './hooks/useGameSocket'
import { useAudioPlayer } from './hooks/useAudioPlayer'
import { useFiveSecondsGame } from './hooks/useFiveSecondsGame'
import { useHangmanGame } from './hooks/useHangmanGame'
import { FiveSecondsGamePage } from './pages/FiveSecondsGamePage'
import { FiveSecondsResultsPage } from './pages/FiveSecondsResultsPage'
import { GamePage } from './pages/GamePage'
import { HangmanGamePage } from './pages/HangmanGamePage'
import { HangmanResultsPage } from './pages/HangmanResultsPage'
import { HistoryPage } from './pages/HistoryPage'
import { MenuPage } from './pages/MenuPage'
import { ResultsPage } from './pages/ResultsPage'
import { SetupPage } from './pages/SetupPage'
import { useAppStore } from './stores/appStore'
import type { GameSessionConfig, SubmitAnswerPayload } from './types/game'

/** Root game app that switches between MVP screens. */
function App() {
  const {
    openHistory,
    resetToMenu: setMenuView,
    selectGame,
    selectMode,
    selectedGame,
    setView,
    setupMode,
    view,
  } = useAppStore()
  const audioPlayer = useAudioPlayer()
  const { error: audioError, isPlaying, playKey, stop } = audioPlayer
  const playComment = useCallback(
    (key: string) => {
      void playKey(key)
    },
    [playKey],
  )
  const gameSocket = useGameSocket({ onCommentKey: playComment })
  const fiveSecondsGame = useFiveSecondsGame()
  const hangmanGame = useHangmanGame()

  const displayedView =
    hangmanGame.snapshot.status === 'finished'
      ? 'hangman_results'
      : fiveSecondsGame.snapshot.status === 'finished'
        ? 'five_seconds_results'
        : gameSocket.snapshot.status === 'finished'
          ? 'results'
          : view

  const startGame = (config: GameSessionConfig) => {
    if (selectedGame === 'five_seconds') {
      void fiveSecondsGame.startSession(config)
      setView('five_seconds_game')
      return
    }

    if (selectedGame === 'hangman') {
      void hangmanGame.startSession(config)
      setView('hangman_game')
      return
    }

    gameSocket.startSession(config)
    setView('game')
  }

  const submitAnswer = (answer: Omit<SubmitAnswerPayload, 'type'>) => {
    gameSocket.submitAnswer(answer)
  }

  const resetToMenu = () => {
    stop()
    gameSocket.reset()
    fiveSecondsGame.reset()
    hangmanGame.reset()
    setMenuView()
  }

  const playAgain = () => {
    stop()
    gameSocket.reset()
    fiveSecondsGame.reset()
    hangmanGame.reset()
    setView('setup')
  }

  return (
    <main className="app-shell">
      <AnimatePresence mode="wait">
        <motion.div
          animate={{ opacity: 1, y: 0 }}
          className="view-motion"
          exit={{ opacity: 0, y: 10 }}
          initial={{ opacity: 0, y: 10 }}
          key={displayedView}
          transition={{ duration: 0.18, ease: 'easeOut' }}
        >
          {displayedView === 'menu' ? (
            <MenuPage
              onOpenHistory={openHistory}
              onSelectGame={selectGame}
              onSelectMode={selectMode}
              selectedGame={selectedGame}
            />
          ) : null}
          {displayedView === 'setup' ? (
            <SetupPage
              game={selectedGame}
              mode={setupMode}
              onBack={resetToMenu}
              onStart={startGame}
            />
          ) : null}
          {displayedView === 'game' ? (
            <GamePage
              audioError={audioError}
              game={gameSocket.snapshot}
              isAudioPlaying={isPlaying}
              onLeave={resetToMenu}
              onSubmitAnswer={submitAnswer}
            />
          ) : null}
          {displayedView === 'five_seconds_game' ? (
            <FiveSecondsGamePage
              game={fiveSecondsGame.snapshot}
              onLeave={resetToMenu}
              onScoreRound={fiveSecondsGame.scoreRound}
            />
          ) : null}
          {displayedView === 'hangman_game' ? (
            <HangmanGamePage
              game={hangmanGame.snapshot}
              onAdvanceRound={hangmanGame.advanceRound}
              onGuessLetter={hangmanGame.guessLetter}
              onLeave={resetToMenu}
            />
          ) : null}
          {displayedView === 'results' ? (
            <ResultsPage
              game={gameSocket.snapshot}
              onBackToMenu={resetToMenu}
              onPlayAgain={playAgain}
            />
          ) : null}
          {displayedView === 'five_seconds_results' ? (
            <FiveSecondsResultsPage
              game={fiveSecondsGame.snapshot}
              onBackToMenu={resetToMenu}
              onPlayAgain={playAgain}
            />
          ) : null}
          {displayedView === 'hangman_results' ? (
            <HangmanResultsPage
              game={hangmanGame.snapshot}
              onBackToMenu={resetToMenu}
              onPlayAgain={playAgain}
            />
          ) : null}
          {displayedView === 'history' ? <HistoryPage onBack={resetToMenu} /> : null}
        </motion.div>
      </AnimatePresence>
    </main>
  )
}

export default App
