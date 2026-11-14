import { useCallback, useEffect, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { useDialog } from '../lib/useDialog'
import { useI18n } from '../i18n/i18n'

export interface Meeting {
  id: string
  starts_at: string
  status: string
  booth?: string | null
  employer_name?: string
}

function MatchDialog({ title, body, cta, onClose }: {
  title: string
  body: ReactNode
  cta: string
  onClose: () => void
}) {
  const ref = useDialog<HTMLDivElement>(onClose)
  return (
    <div role="dialog" aria-modal="true" aria-label={title}
         className="fixed inset-0 z-[70] p-4 flex items-center justify-center"
         style={{ background: 'rgba(23,23,23,0.35)' }}
         onClick={(e) => { if (e.target === e.currentTarget) onClose() }}>
      <div ref={ref} className="card p-5 w-full max-w-sm text-center">
        <h2 className="mt-0">{title}</h2>
        <p>{body}</p>
        <button type="button" className="btn btn-primary w-full"
                style={{ minHeight: 48 }} onClick={onClose}>
          {cta}
        </button>
      </div>
    </div>
  )
}

/** Card-at-a-time chooser (§8.3). Generic over the item type — the page
    supplies the card renderer, the choose action and i18n text. */
export default function CardChooser<T>({ items, chosen, renderCard, onChoose,
  onTakeBack, renderChosenRow, chosenCount, limit, storageKey, chooseLabel,
  skipLabel, counter, counterChosen, listLabel, cardsLabel, maxText,
  match, listView, noCards, idOf }: {
  items: T[]
  chosen: T[]
  renderCard: (item: T, current: boolean) => ReactNode
  onChoose: (item: T) => Promise<{ meeting?: Meeting | null } | void>
  onTakeBack?: (item: T) => Promise<void>
  renderChosenRow: (item: T) => ReactNode
  chosenCount: number
  limit: number
  storageKey: string
  chooseLabel: string
  skipLabel: string
  counter: (i: number, n: number) => string   // "3 of 12"
  counterChosen: (a: number, b: number) => string // "Chosen 2 of 5"
  listLabel: string                            // "Show as a list"
  cardsLabel: string                           // "Show one card at a time"
  maxText: string                              // "You chose 5 — that's the most"
  match?: (meeting: Meeting, item: T) => { title: string; body: ReactNode } | null
  listView?: ReactNode
  noCards?: ReactNode
  idOf: (item: T) => string
}) {
  const { t } = useI18n()
  const skipKey = `${storageKey}:skip`
  const listKey = `${storageKey}:list`
  const [skipped, setSkipped] = useState<string[]>(() => {
    try { return JSON.parse(localStorage.getItem(skipKey) ?? '[]') }
    catch { return [] }
  })
  const [listMode, setListMode] = useState(
    () => localStorage.getItem(listKey) === '1')
  const [reviewSkipped, setReviewSkipped] = useState(false)
  const [idx, setIdx] = useState(0)
  const [busy, setBusy] = useState(false)
  const [matchInfo, setMatchInfo] = useState<
    { title: string; body: ReactNode } | null>(null)
  const rootRef = useRef<HTMLDivElement>(null)

  const skip = useCallback((id: string) => {
    setSkipped((s) => {
      const next = [...s, id]
      try { localStorage.setItem(skipKey, JSON.stringify(next)) }
      catch { /* full */ }
      return next
    })
    setReviewSkipped(false)
  }, [skipKey])

  const skippedSet = new Set(skipped)
  const pool = reviewSkipped
    ? items.filter((it) => skippedSet.has(idOf(it)))
    : items.filter((it) => !skippedSet.has(idOf(it)))
  const shown = Math.min(idx, Math.max(0, pool.length - 1))
  const item = pool[shown]

  // reset position when the pool changes (choose/take-back/list switch)
  useEffect(() => { setIdx(0) }, [items.length, reviewSkipped, listMode])

  const choose = async () => {
    if (!item || busy) return
    setBusy(true)
    try {
      const r = await onChoose(item)
      if (r?.meeting && match) {
        const m = match(r.meeting, item)
        if (m) setMatchInfo(m)
      }
    } finally { setBusy(false) }
  }

  const onKey = useCallback((e: React.KeyboardEvent) => {
    const el = e.target as HTMLElement
    if (/^(INPUT|TEXTAREA|SELECT)$/.test(el.tagName)) return
    if (e.key === 'ArrowRight') { e.preventDefault(); choose() }
    else if (e.key === 'ArrowLeft' && item) {
      e.preventDefault(); skip(idOf(item))
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [item, busy])

  const toggleList = () => {
    setListMode((v) => {
      try { localStorage.setItem(listKey, v ? '0' : '1') } catch { /* */ }
      return !v
    })
  }

  const atMax = limit > 0 && chosenCount >= limit

  return (
    <div ref={rootRef} onKeyDown={onKey} className="grid gap-3">
      <div className="flex gap-2 items-center flex-wrap">
        {!listMode && item && (
          <span className="text-secondary">{counter(shown + 1, pool.length)}</span>
        )}
        <span className="text-secondary">
          {counterChosen(chosenCount, limit)}</span>
        {listView != null && (
          <button type="button" className="btn btn-quiet ms-auto"
                  onClick={toggleList} aria-pressed={listMode}>
            {listMode ? cardsLabel : listLabel}</button>
        )}
      </div>

      {listMode && listView ? listView : atMax ? (
        <div className="card p-4 grid gap-2">
          <p className="m-0 font-medium">{maxText}</p>
          <ul className="m-0 p-0 list-none grid gap-2">
            {chosen.map((c) => (
              <li key={idOf(c)} className="flex gap-2 items-center flex-wrap">
                <span className="flex-1" style={{ minWidth: 120 }}>
                  {renderChosenRow(c)}</span>
                {onTakeBack && (
                  <button type="button" className="btn btn-secondary"
                          style={{ minHeight: 44 }}
                          onClick={() => onTakeBack(c)}>
                    {t('ev.notinterested')}</button>
                )}
              </li>
            ))}
          </ul>
        </div>
      ) : !item ? (
        <div className="grid gap-2">
          {noCards ?? <p className="text-secondary">{t('choose.done')}</p>}
          {skipped.length > 0 && (
            <button type="button" className="btn btn-secondary"
                    onClick={() => { setReviewSkipped(true); setIdx(0) }}>
              {t('choose.skipped', { n: skipped.length })}</button>
          )}
        </div>
      ) : (
        <div className="chooser-slide" key={idOf(item)}>
          {renderCard(item, true)}
          <div className="chooser-btns">
            <button type="button" className="btn btn-secondary"
                    onClick={() => skip(idOf(item))} disabled={busy}>
              {skipLabel}</button>
            <button type="button" className="btn btn-primary"
                    onClick={choose} disabled={busy}>
              {chooseLabel}</button>
          </div>
        </div>
      )}

      {item && !listMode && !atMax && skipped.length > 0 &&
        !reviewSkipped && (
        <button type="button" className="btn btn-quiet justify-self-start"
                onClick={() => { setReviewSkipped(true); setIdx(0) }}>
          {t('choose.skipped', { n: skipped.length })}</button>
      )}
      {reviewSkipped && item && (
        <p className="m-0 text-secondary">{t('choose.reviewing')}</p>
      )}

      {matchInfo && (
        <MatchDialog title={matchInfo.title} body={matchInfo.body}
                     cta={t('common.ok')} onClose={() => setMatchInfo(null)} />
      )}
    </div>
  )
}
