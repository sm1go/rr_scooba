import { createContext, useContext, useEffect, useState, type ReactNode } from 'react'
import en, { type Key } from './en'
import fi from './fi'
import sv from './sv'
import ru from './ru'
import ar from './ar'
import et from './et'
import zh from './zh'
import fa from './fa'
import sq from './sq'
import uk from './uk'

export type Lang = 'en' | 'fi' | 'sv' | 'ru' | 'ar' | 'et' | 'zh' | 'fa' | 'sq' | 'uk'

/** Native names shown in the language menu (spec §3). */
export const LANGS: { id: Lang; name: string; rtl?: boolean }[] = [
  { id: 'en', name: 'English' },
  { id: 'fi', name: 'Suomi' },
  { id: 'sv', name: 'Svenska' },
  { id: 'ru', name: 'Русский' },
  { id: 'ar', name: 'العربية', rtl: true },
  { id: 'et', name: 'Eesti' },
  { id: 'zh', name: '中文' },
  { id: 'fa', name: 'فارسی', rtl: true },
  { id: 'sq', name: 'Shqip' },
  { id: 'uk', name: 'Українська' },
]

// en and fi are complete; the other locale files are machine-drafted and
// fall back to English key by key until native review.
const dicts: Record<Lang, Record<Key, string>> = {
  en, fi,
  sv: { ...en, ...sv } as Record<Key, string>,
  ru: { ...en, ...ru } as Record<Key, string>,
  ar: { ...en, ...ar } as Record<Key, string>,
  et: { ...en, ...et } as Record<Key, string>,
  zh: { ...en, ...zh } as Record<Key, string>,
  fa: { ...en, ...fa } as Record<Key, string>,
  sq: { ...en, ...sq } as Record<Key, string>,
  uk: { ...en, ...uk } as Record<Key, string>,
}
const LANG_KEY = 'ewm.lang'

interface I18nCtx {
  lang: Lang
  setLang: (l: Lang) => void
  t: (key: Key, vars?: Record<string, string | number>) => string
}

const Ctx = createContext<I18nCtx | null>(null)

export function I18nProvider({ children }: { children: ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => {
    const l = localStorage.getItem(LANG_KEY) as Lang
    return LANGS.some((x) => x.id === l) ? l : 'en'
  })

  const setLang = (l: Lang) => {
    localStorage.setItem(LANG_KEY, l)
    setLangState(l)
  }

  const rtl = LANGS.find((l) => l.id === lang)?.rtl
  useEffect(() => {
    document.documentElement.lang = lang
    document.documentElement.dir = rtl ? 'rtl' : 'ltr'
  }, [lang, rtl])

  const t = (key: Key, vars?: Record<string, string | number>) => {
    let s = dicts[lang][key] ?? dicts.en[key] ?? key
    if (vars) for (const [k, v] of Object.entries(vars)) s = s.replace(`{${k}}`, String(v))
    return s
  }

  return <Ctx.Provider value={{ lang, setLang, t }}>{children}</Ctx.Provider>
}

export function useI18n() {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useI18n outside provider')
  return ctx
}
