const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

type SttResponse = {
  text: string
}

export async function transcribeAudio(audio: Blob): Promise<string> {
  const formData = new FormData()
  formData.append('file', audio, 'answer.webm')

  const response = await fetch(`${API_BASE_URL}/api/stt`, {
    method: 'POST',
    body: formData,
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || `STT request failed: ${response.status}`)
  }

  const payload = (await response.json()) as SttResponse
  return payload.text
}
