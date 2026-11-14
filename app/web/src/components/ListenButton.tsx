import { useEffect, useState } from 'react'
import { useI18n } from '../i18n/i18n'

/** Reads text aloud with speechSynthesis in the UI language. */
export default function ListenButton({ text }: { text: string }) {
  const { t, lang } = useI18n()
  const [speaking, setSpeaking] = useState(false)
  const supported = typeof speechSynthesis !== 'undefined'

  useEffect(() => () => {
    if (supported) speechSynthesis.cancel()
  }, [supported])

  if (!supported) return null

  const toggle = () => {
    if (speaking) {
      speechSynthesis.cancel()
      setSpeaking(false)
      return
    }
    const u = new SpeechSynthesisUtterance(text)
    u.lang = lang === 'fi' ? 'fi-FI' : 'en-GB'
    u.rate = 0.95
    u.onend = () => setSpeaking(false)
    u.onerror = () => setSpeaking(false)
    speechSynthesis.cancel()
    speechSynthesis.speak(u)
    setSpeaking(true)
  }

  return (
    <button type="button" className="btn btn-quiet listen-btn"
            onClick={toggle} aria-pressed={speaking}
            style={{ minHeight: 48 }}>
      {speaking ? t('common.stop') : t('common.listen')}
    </button>
  )
}
