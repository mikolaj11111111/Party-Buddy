import { useCallback, useState } from 'react'

import './App.css'
import { useGameSocket } from './hooks/useGameSocket'
import { useAudioPlayer } from './hooks/useAudioPlayer'
import { GamePage } from './pages/GamePage'
import { HistoryPage } from './pages/HistoryPage'
import { MenuPage } from './pages/MenuPage'
import { ResultsPage } from './pages/ResultsPage'
import { SetupPage } from './pages/SetupPage'
import type { GameSessionConfig, SubmitAnswerPayload } from './types/game'

type AppView = 'menu' | 'setup' | 'game' | 'results' | 'history'
type SetupMode = 'solo' | 'hotseat'

/** Root game app that switches between MVP screens. */
function App() {
  const [view, setView] = useState<AppView>('menu')
  const [setupMode, setSetupMode] = useState<SetupMode>('hotseat')
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

  const selectMode = (mode: SetupMode) => {
    setSetupMode(mode)
    setView('setup')
  }

  const openHistory = () => {
    setView('history')
  }

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
    setView('menu')
  }

  const playAgain = () => {
    stop()
    gameSocket.reset()
    setView('setup')
  }

  return (
    <main className="app-shell">
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
    </main>
  )
}

export default App
