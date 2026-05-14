import { useEffect, useState } from 'react'

/** Calculate whole seconds left until an ISO timestamp deadline. */
const getSecondsLeft = (deadlineAt: string | null, now: number) => {
  if (!deadlineAt) {
    return 0
  }

  const diff = new Date(deadlineAt).getTime() - now
  return Math.max(0, Math.ceil(diff / 1000))
}

/** Keep a local visual countdown in sync with the backend deadline. */
export function useCountdown(deadlineAt: string | null) {
  const [now, setNow] = useState(() => Date.now())

  useEffect(() => {
    if (!deadlineAt) {
      return undefined
    }

    const updateNow = () => setNow(Date.now())
    const timeoutId = window.setTimeout(updateNow, 0)
    const intervalId = window.setInterval(updateNow, 250)

    return () => {
      window.clearTimeout(timeoutId)
      window.clearInterval(intervalId)
    }
  }, [deadlineAt])

  return getSecondsLeft(deadlineAt, now)
}
