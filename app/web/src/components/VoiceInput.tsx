import { useState } from 'react'
import { Mic } from 'lucide-react'
import { useI18n } from '../i18n/i18n'

const SPEECH_LANGS = [
  { id: 'fi-FI', name: 'Suomi' }, { id: 'en-GB', name: 'English' },
  { id: 'sv-SE', name: 'Svenska' }, { id: 'ar-SA', name: 'العربية' },
  { id: 'uk-UA', name: 'Українська' }, { id: 'ru-RU', name: 'Русский' },
  { id: 'et-EE', name: 'Eesti' }, { id: 'so-SO', name: 'Soomaali' },
]

interface SR extends EventTarget {
  lang: string
  continuous: boolean
  interimResults: boolean
  start: () => void
  stop: () => void
  onresult: ((e: { results: { [i: number]: { [i: number]: { transcript: string } } } }) => void) | null
  onend: (() => void) | null
}

declare global {
  interface Window {
    SpeechRecognition?: new () => SR
    webkitSpeechRecognition?: new () => SR
  }
}

/** "Speak instead of typing" — appends recognised text to the textarea.
    compact: mic button + language only, for a one-line search box. */
export default function VoiceInput({
  onText, targetId, compact,
}: { onText: (text: string) => void; targetId: string; compact?: boolean }) {
  const { t, lang: ui } = useI18n()
  const [lang, setLang] = useState(
    SPEECH_LANGS.find((l) => l.id.startsWith(ui))?.id ?? 'fi-FI')
  const [listening, setListening] = useState(false)
  const [rec, setRec] = useState<SR | null>(null)

  const Ctor = window.SpeechRecognition ?? window.webkitSpeechRecognition
  if (!Ctor) {
    if (compact) return null
    return <p className="text-secondary" style={{ fontSize: '1rem' }}>
      {t('apply.voiceunsupported')}</p>
  }

  const toggle = () => {
    if (listening && rec) {
      rec.stop()
      return
    }
    const r = new Ctor()
    r.lang = lang
    r.continuous = false
    r.interimResults = false
    r.onresult = (e) => {
      const text = e.results[0]?.[0]?.transcript
      if (text) onText(text)
    }
    r.onend = () => { setListening(false); setRec(null) }
    r.start()
    setRec(r)
    setListening(true)
  }

  return (
    <div className={compact ? 'contents' : 'flex flex-wrap items-center gap-2 mt-2'}>
      <button type="button" className={`btn ${compact ? 'btn-secondary' : 'btn-quiet'}`}
              onClick={toggle} aria-pressed={listening} aria-controls={targetId}
              style={{ minHeight: 48 }}>
        <Mic size={20} aria-hidden="true" />
        {listening ? t('common.stop') : t(compact ? 'jobs.speak' : 'apply.speak')}
      </button>
      <label className="text-secondary" style={{ fontSize: '1rem' }}>
        <select value={lang} onChange={(e) => setLang(e.target.value)}
                aria-label="Spoken language"
                className="card px-3 py-2" style={{ minHeight: 48 }}>
          {SPEECH_LANGS.map((l) => (
            <option key={l.id} value={l.id}>{l.name}</option>
          ))}
        </select>
      </label>
      {(!compact || listening) && (
        <p className="text-secondary w-full" style={{ fontSize: '1rem' }}>
          {t('apply.voiceprivacy')}
        </p>
      )}
    </div>
  )
}
