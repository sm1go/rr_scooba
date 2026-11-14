import { useCallback, useEffect, useState } from 'react'

/** Load data once (and on demand via reload). Errors are surfaced as text. */
export function useLoad<T>(fn: () => Promise<T>, deps: unknown[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [error, setError] = useState<string | null>(null)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const run = useCallback(fn, deps)
  const reload = useCallback(() => {
    setError(null)
    run()
      .then(setData)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : 'Something went wrong.'))
  }, [run])
  useEffect(() => {
    reload()
  }, [reload])
  return { data, setData, error, reload }
}
