import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import en, { type Key } from './en'
import fi from './fi'

export type Lang = 'en' | 'fi'
const dicts: Record<Lang, Record<Key, string>> = { en, fi }
const LANG_KEY = 'ewm.lang'

interface I18nCtx {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: Key) => string
}

const Ctx = createContext<I18nCtx | null>(null)

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(
    () => (localStorage.getItem(LANG_KEY) as Lang) || 'en')

  const setLang = (l: Lang) => {
    localStorage.setItem(LANG_KEY, l)
    setLangState(l)
  }

  useEffect(() => {
    document.documentElement.lang = lang
  }, [lang])

  const t = (key: Key) => dicts[lang][key] ?? dicts.en[key] ?? key

  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>
}

export function useI18n() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useI18n outside provider')
  return ctx
}
