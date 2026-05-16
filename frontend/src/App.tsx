import { useCallback } from 'react'
import { AnimatePresence, motion } from 'motion/react'

import './App.css'
import { useGameSocket } from './hooks/useGameSocket'
import { useAudioPlayer } from './hooks/useAudioPlayer'
import { GamePage } from './pages/GamePage'
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
    selectMode,
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

  const displayedView = gameSocket.snapshot.status === 'finished' ? 'results' : view

  const startGame = (config: GameSessionConfig) => {
    gameSocket.startSession(config)
    setView('game')
  }

  const submitAnswer = (answer: Omit<SubmitAnswerPayload, 'type'>) => {
    gameSocket.submitAnswer(answer)
  }

  const resetToMenu = () => {
    stop()
    gameSocket.reset()
    setMenuView()
  }

  const playAgain = () => {
    stop()
    gameSocket.reset()
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
            <MenuPage onOpenHistory={openHistory} onSelectMode={selectMode} />
          ) : null}
          {displayedView === 'setup' ? (
            <SetupPage mode={setupMode} onBack={resetToMenu} onStart={startGame} />
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
          {displayedView === 'results' ? (
            <ResultsPage
              game={gameSocket.snapshot}
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
