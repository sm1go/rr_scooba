import { useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2, GraduationCap, Check } from 'lucide-react'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { NeedEntry } from '../types'
import CompanyLogo from './CompanyLogo'

const ucfirst = (s: string) =>
  s ? s[0].toLocaleUpperCase() + s.slice(1) : s

/** One translated fit-reason chip. */
function Fit({ f }: { f: { key: string; [k: string]: unknown } }) {
  const { t } = useI18n()
  const text = t(`ev.fit.${f.key}` as Key, f as Record<string, string>)
  return <span className="chip yes">{text}</span>
}

/** Employer need card — used on event pages and the company profile. */
export default function NeedCardView({ e, registered, onToggleInterest,
  interestCount, limit, onMeetsChange }: {
  e: NeedEntry
  registered?: boolean
  interestCount?: number
  limit?: number
  onToggleInterest?: (e: NeedEntry) => void
  onMeetsChange?: (meets: number[]) => void
}) {
  const { t } = useI18n()
  const card = e.need!.card
  const [meets, setMeets] = useState<number[]>(e.meets ?? [])
  const [open, setOpen] = useState(false)

  // group languages that share the same task
  const langGroups = new Map<string, string[]>()
  for (const l of card.languages) {
    const task = l.task || ''
    langGroups.set(task, [...(langGroups.get(task) ?? []),
                          `${l.name} ${l.level}`])
  }

  return (
    <article className="card p-5 grid gap-4">
      <header className="flex gap-3 items-start flex-wrap">
        <CompanyLogo
          employer={{ name: e.employer_name ?? '',
                      logo_color: e.logo_color, field: e.field }}
          size={40} />
        <div className="flex-1" style={{ minWidth: 0 }}>
          <h3 className="m-0">
            <Link to={`/companies/${e.employer_id}`}>
              {e.employer_name}</Link>
          </h3>
          {e.need!.need_by === 'advisor' && (
            <p className="text-secondary m-0" style={{ fontSize: '.9rem' }}>
              {t('ev.byadvisor')}</p>
          )}
        </div>
        {e.booth && <span className="chip">{e.booth}</span>}
        {e.company_badges?.includes('employer_answered') && (
          <span className="chip yes">
            <Check size={14} aria-hidden="true" />
            {t('badge.employer_answered')}</span>
        )}
      </header>

      <div className="need-cols">
        {card.first_week.length > 0 && (
          <div>
            <strong className="block mb-1">{t('ev.firstweek')}</strong>
            <ul className="m-0 p-0 list-none grid gap-1 need-list">
              {card.first_week.map((x, i) => (
                <li key={i}>
                  <CheckCircle2 size={15} aria-hidden="true" />
                  <span>{x}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
        {card.must_haves.length > 0 && (
          <div>
            <strong className="block mb-1">{t('ev.must')}</strong>
            <ul className="m-0 p-0 list-none grid gap-3">
              {card.must_haves.map((m, i) => (
                <li key={i} className="flex gap-2 items-start">
                  <span className="flex-1" style={{ minWidth: 0 }}>
                    <span className="block font-medium">
                      {ucfirst(m.text)}</span>
                    {m.why && (
                      <span className="block text-secondary">
                        {t('ev.why')} {m.why}</span>
                    )}
                  </span>
                  {registered && e.interested !== undefined && (
                    <label className="need-fitsme">
                      <input type="checkbox" checked={meets.includes(i)}
                             onChange={() => {
                               const next = meets.includes(i)
                                 ? meets.filter((x) => x !== i)
                                 : [...meets, i]
                               setMeets(next)
                               onMeetsChange?.(next)
                             }} />
                      <span>{t('ev.thisisme')}</span>
                    </label>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {card.languages.length > 0 && (
        <div className="flex gap-2 flex-wrap items-center">
          <strong>{t('ev.langs')}</strong>
          {[...langGroups.entries()].map(([task, langs], i) => (
            <span key={i}>
              {langs.map((lg, j) => (
                <span key={j} className="chip me-1">{lg}</span>
              ))}
              {task && <span className="text-secondary">— {task}</span>}
            </span>
          ))}
        </div>
      )}

      {card.will_teach.length > 0 && (
        <div>
          <strong className="block mb-1">{t('ev.teach')}</strong>
          <ul className="m-0 p-0 list-none grid gap-1 need-list">
            {card.will_teach.map((x, i) => (
              <li key={i}>
                <GraduationCap size={15} aria-hidden="true" />
                <span>{x}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {e.fit && e.fit.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {e.fit.map((f, i) => <Fit key={i} f={f} />)}
        </div>
      )}

      {registered && onToggleInterest && (
        <div className="flex gap-2 items-center flex-wrap">
          {!e.interested && (interestCount ?? 0) >= (limit ?? 5) ? null
          : !e.interested && !open ? (
            <button type="button" className="btn btn-primary"
                    onClick={() => setOpen(true)}>{t('ev.interested')}</button>
          ) : e.interested ? (
            <>
              <span className="font-medium"
                    style={{ color: 'var(--color-brand)' }}>
                {t('ev.interested_on')}</span>
              <button type="button" className="btn btn-secondary"
                      onClick={() => onToggleInterest(e)}>
                {t('ev.notinterested')}</button>
            </>
          ) : (
            <button type="button" className="btn btn-primary"
                    onClick={() => onToggleInterest({ ...e, meets })}>
              {t('ev.interested.send')}
            </button>
          )}
        </div>
      )}
    </article>
  )
}
