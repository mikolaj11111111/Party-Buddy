import { useRef, useState } from 'react'

import { transcribeAudio } from '../api/stt'

type MicButtonProps = {
  onTranscript: (text: string) => void
}

type MicState = 'idle' | 'recording' | 'uploading' | 'error'

/** Pick the best MediaRecorder options supported by the browser. */
const getRecorderOptions = (): MediaRecorderOptions | undefined => {
  const mimeTypes = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/ogg;codecs=opus',
    'audio/mp4',
  ]
  const mimeType = mimeTypes.find((candidate) =>
    MediaRecorder.isTypeSupported(candidate),
  )

  if (!mimeType) {
    return undefined
  }

  return { mimeType }
}

/** Convert browser microphone failures into user-facing copy. */
const getRecordingErrorMessage = (recordingError: unknown) => {
  if (recordingError instanceof DOMException) {
    if (
      recordingError.name === 'NotAllowedError' ||
      recordingError.name === 'SecurityError'
    ) {
      return 'Przegladarka zablokowala mikrofon. Sprawdz uprawnienia przy adresie strony.'
    }

    if (recordingError.name === 'NotFoundError') {
      return 'Nie wykryto mikrofonu.'
    }

    if (recordingError.name === 'NotReadableError') {
      return 'Mikrofon jest zajety przez inna aplikacje.'
    }

    if (recordingError.name === 'NotSupportedError') {
      return 'Ta przegladarka nie obsluguje aktualnego formatu nagrywania.'
    }
  }

  if (recordingError instanceof Error) {
    return `Nie udalo sie uruchomic mikrofonu: ${recordingError.message}`
  }

  return 'Nie udalo sie uruchomic mikrofonu.'
}

/** Record push-to-talk audio and submit it to STT after release. */
export function MicButton({ onTranscript }: MicButtonProps) {
  const [state, setState] = useState<MicState>('idle')
  const [error, setError] = useState<string | null>(null)
  const recorderRef = useRef<MediaRecorder | null>(null)
  const streamRef = useRef<MediaStream | null>(null)
  const chunksRef = useRef<BlobPart[]>([])

  // Stop microphone tracks so the browser releases the device.
  const releaseStream = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop())
    streamRef.current = null
  }

  // Request microphone access and start collecting audio chunks.
  const startRecording = async () => {
    if (state !== 'idle' && state !== 'error') {
      return
    }

    setError(null)

    if (!navigator.mediaDevices?.getUserMedia) {
      setState('error')
      setError('Ta przegladarka nie obsluguje nagrywania.')
      return
    }

    if (typeof MediaRecorder === 'undefined') {
      setState('error')
      setError('Ta przegladarka nie obsluguje MediaRecorder.')
      return
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      const recorderOptions = getRecorderOptions()
      const recorder = recorderOptions
        ? new MediaRecorder(stream, recorderOptions)
        : new MediaRecorder(stream)

      streamRef.current = stream
      recorderRef.current = recorder
      chunksRef.current = []

      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data)
        }
      }

      recorder.onstop = async () => {
        setState('uploading')
        releaseStream()

        try {
          const audio = new Blob(chunksRef.current, { type: recorder.mimeType })
          const text = await transcribeAudio(audio)
          onTranscript(text)
          setState('idle')
        } catch (requestError) {
          setState('error')
          setError(
            requestError instanceof Error
              ? requestError.message
              : 'Nie udalo sie rozpoznac audio.',
          )
        }
      }

      recorder.start()
      setState('recording')
    } catch (recordingError) {
      releaseStream()
      setState('error')
      setError(getRecordingErrorMessage(recordingError))
    }
  }

  // Finish the current recording when the user releases the button.
  const stopRecording = () => {
    if (recorderRef.current?.state === 'recording') {
      recorderRef.current.stop()
    }
  }

  const isBusy = state === 'recording' || state === 'uploading'
  const label =
    state === 'recording'
      ? 'Pusc, aby wyslac'
      : state === 'uploading'
        ? 'Wysylam...'
        : 'Przytrzymaj i mow'

  return (
    <div className="mic-panel">
      <button
        type="button"
        className={`mic-button mic-button--${state}`}
        disabled={state === 'uploading'}
        aria-pressed={state === 'recording'}
        onPointerDown={startRecording}
        onPointerUp={stopRecording}
        onPointerCancel={stopRecording}
        onPointerLeave={stopRecording}
      >
        <span className="mic-button__dot" aria-hidden="true" />
        <span>{label}</span>
      </button>
      <div className="mic-status" aria-live="polite">
        {isBusy && state === 'recording' ? 'Nagrywam' : null}
        {isBusy && state === 'uploading' ? 'Rozpoznaje' : null}
        {state === 'error' ? error : null}
      </div>
    </div>
  )
}
