import {
  createContext, useContext, useEffect, useState, type ReactNode,
} from 'react'

export interface A11ySettings {
  textSize: 'normal' | 'large' | 'xlarge'
  contrast: boolean
  easierReading: boolean
  reduceMotion: boolean
  listen: boolean
}

const DEFAULTS: A11ySettings = {
  textSize: 'normal', contrast: false, easierReading: false,
  reduceMotion: false, listen: true,
}
const KEY = 'ewm.a11y'

interface A11yCtx {
  settings: A11ySettings
  set: <K extends keyof A11ySettings>(k: K, v: A11ySettings[K]) => void
  open: boolean
  setOpen: (o: boolean) => void
}

const Ctx = createContext<A11yCtx | null>(null)

function load(): A11ySettings {
  try {
    return { ...DEFAULTS, ...JSON.parse(localStorage.getItem(KEY) || '{}') }
  } catch {
    return DEFAULTS
  }
}

export function A11yProvider({ children }: { children: ReactNode }) {
  const [settings, setSettings] = useState<A11ySettings>(load)
  const [open, setOpen] = useState(false)

  const set = <K extends keyof A11ySettings>(k: K, v: A11ySettings[K]) => {
    setSettings((s) => {
      const next = { ...s, [k]: v }
      localStorage.setItem(KEY, JSON.stringify(next))
      return next
    })
  }

  useEffect(() => {
    const el = document.documentElement
    el.dataset.textSize = settings.textSize
    el.dataset.contrast = settings.contrast ? 'high' : 'normal'
    el.dataset.reading = settings.easierReading ? 'easier' : 'normal'
    el.dataset.motion = settings.reduceMotion ? 'reduce' : 'normal'
    el.dataset.listen = settings.listen ? 'on' : 'off'
  }, [settings])

  return (
    <Ctx.Provider value={{ settings, set, open, setOpen }}>
      {children}
    </Ctx.Provider>
  )
}

export function useA11y() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useA11y outside provider')
  return ctx
}
