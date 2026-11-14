import { useEffect, useRef } from 'react'

const FOCUSABLE = 'a[href],button:not([disabled]),input:not([disabled]),'
  + 'select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])'

/** Modal dialog behaviour: focus first control, trap Tab, Escape closes,
    focus returns to the opener when the dialog unmounts. */
export function useDialog<T extends HTMLElement>(onClose: () => void) {
  const ref = useRef<T>(null)
  const close = useRef(onClose)
  useEffect(() => { close.current = onClose })
  useEffect(() => {
    const opener = document.activeElement as HTMLElement | null
    const el = ref.current
    el?.querySelector<HTMLElement>(FOCUSABLE)?.focus()
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') { e.preventDefault(); close.current(); return }
      if (e.key !== 'Tab' || !el) return
      const items = [...el.querySelectorAll<HTMLElement>(FOCUSABLE)]
      if (!items.length) return
      const first = items[0], last = items[items.length - 1]
      const a = document.activeElement
      if (!el.contains(a)) { e.preventDefault(); first.focus() }
      else if (e.shiftKey && a === first) { e.preventDefault(); last.focus() }
      else if (!e.shiftKey && a === last) { e.preventDefault(); first.focus() }
    }
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('keydown', onKey)
      const a = document.activeElement
      if (!a || a === document.body || el?.contains(a)) opener?.focus?.()
    }
  }, [])
  return ref
}
