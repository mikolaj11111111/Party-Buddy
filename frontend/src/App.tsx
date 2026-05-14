import { useState } from 'react'

import './App.css'
import { MicButton } from './components/MicButton'
import { useAudioPlayer } from './hooks/useAudioPlayer'

const INTRO_TTS_KEY = '87565612ac80dc0017c62c42ab957b7b97683e39783bdb4bb058e78031d8ee8b'

/** Minimal local workbench for STT recording and TTS playback smoke tests. */
function App() {
  const [transcript, setTranscript] = useState('')
  const audioPlayer = useAudioPlayer()

  return (
    <main className="app-shell">
      <section className="stt-workbench">
        <header className="stt-header">
          <p className="eyebrow">M4 Audio</p>
          <h1>Test glosu i odpowiedzi</h1>
        </header>

        <MicButton onTranscript={setTranscript} />

        <section className="transcript-panel" aria-live="polite">
          <p className="panel-label">Ostatni tekst</p>
          <p className="transcript-text">{transcript || 'Nagraj odpowiedz glosowa.'}</p>
        </section>

        <section className="transcript-panel tts-panel" aria-live="polite">
          <p className="panel-label">Komentarz TTS</p>
          <div className="button-row">
            <button
              type="button"
              className="secondary-button"
              disabled={audioPlayer.isPlaying}
              onClick={() => void audioPlayer.playKey(INTRO_TTS_KEY)}
            >
              {audioPlayer.isPlaying ? 'Odtwarzam...' : 'Odtworz intro'}
            </button>
            <button
              type="button"
              className="secondary-button secondary-button--muted"
              disabled={!audioPlayer.isPlaying}
              onClick={audioPlayer.stop}
            >
              Stop
            </button>
          </div>
          <p className="mic-status">{audioPlayer.error}</p>
        </section>
      </section>
    </main>
  )
}

export default App
