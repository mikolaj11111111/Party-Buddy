import { useState } from 'react'

import './App.css'
import { MicButton } from './components/MicButton'

function App() {
  const [transcript, setTranscript] = useState('')

  return (
    <main className="app-shell">
      <section className="stt-workbench">
        <header className="stt-header">
          <p className="eyebrow">M3 STT</p>
          <h1>Rozpoznawanie odpowiedzi</h1>
        </header>

        <MicButton onTranscript={setTranscript} />

        <section className="transcript-panel" aria-live="polite">
          <p className="panel-label">Ostatni tekst</p>
          <p className="transcript-text">{transcript || 'Nagraj odpowiedz glosowa.'}</p>
        </section>
      </section>
    </main>
  )
}

export default App
