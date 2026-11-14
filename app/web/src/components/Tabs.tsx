import { useRef, useState } from 'react'
import type { KeyboardEvent, ReactNode } from 'react'

/** Accessible tab set: real tablist/tab/tabpanel with arrow-key support. */
export function Tabs({ labels, children, label, initial = 0 }: {
  labels: string[]; children: ReactNode[]; label: string; initial?: number
}) {
  const [active, setActive] = useState(initial)
  const refs = useRef<(HTMLButtonElement | null)[]>([])

  const onKey = (i: number) => (e: KeyboardEvent) => {
    let n = -1
    if (e.key === 'ArrowRight' || e.key === 'ArrowDown') n = (i + 1) % labels.length
    if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') n = (i - 1 + labels.length) % labels.length
    if (e.key === 'Home') n = 0
    if (e.key === 'End') n = labels.length - 1
    if (n >= 0) {
      e.preventDefault()
      refs.current[n]?.focus()
      setActive(n)
    }
  }

  return (
    <div>
      <div role="tablist" aria-label={label}
           className="flex gap-1 flex-wrap"
           style={{ borderBottom: '2px solid var(--color-hairline)' }}>
        {labels.map((l, i) => (
          <button key={l} type="button" role="tab" id={`tab-${i}`}
                  ref={(el) => { refs.current[i] = el }}
                  aria-selected={active === i} aria-controls={`panel-${i}`}
                  tabIndex={active === i ? 0 : -1}
                  onClick={() => setActive(i)} onKeyDown={onKey(i)}
                  className="px-4 py-2 font-semibold"
                  style={{
                    minHeight: 44, border: 'none', background: 'none',
                    cursor: 'pointer',
                    color: active === i ? 'var(--color-ink)' : 'var(--color-secondary)',
                    borderBottom: active === i
                      ? '3px solid var(--color-ink)'
                      : '3px solid transparent',
                    marginBottom: -2,
                  }}>
            {l}
          </button>
        ))}
      </div>
      {children.map((c, i) => (
        <div key={i} role="tabpanel" id={`panel-${i}`}
             aria-labelledby={`tab-${i}`} hidden={active !== i}
             className="pt-5">
          {c}
        </div>
      ))}
    </div>
  )
}
