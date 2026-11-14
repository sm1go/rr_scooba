import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { EventPlan } from '../types'

/** /event/print — the visitor's plan in an A4-friendly layout. */
export default function EventPrint() {
  const { t } = useI18n()
  const [plan, setPlan] = useState<EventPlan | null>(null)
  const [err, setErr] = useState(false)

  useEffect(() => {
    api<EventPlan>('/api/me/event-plan').then(setPlan).catch(() => setErr(true))
  }, [])

  if (err) return <p>{t('common.error')}</p>
  if (!plan) return <p>{t('common.loading')}</p>

  return (
    <div className="print-sheet max-w-3xl mx-auto">
      <div className="no-print flex justify-between items-center mb-4">
        <Link to="/event" className="text-secondary">{`← ${t('common.back')}`}</Link>
        <button type="button" className="btn btn-primary" onClick={() => window.print()}>
          {t('print.print')}
        </button>
      </div>
      <h1 data-page-title tabIndex={-1}>{plan.event?.name ?? t('event.title')}</h1>
      <p className="text-secondary">{plan.event?.date} · {plan.event?.venue}</p>

      <div className="card p-6 text-center my-5">
        <p className="m-0 text-secondary">{t('event.number')}</p>
        <p className="m-0 font-display" style={{ fontSize: '5rem', lineHeight: 1.1 }}>
          {plan.code}
        </p>
        <p className="m-0 mt-2">{t('event.numberwhy')}</p>
      </div>

      <h2>{t('event.myplan')}</h2>
      <ul className="m-0 p-0 list-none">
        {plan.booths.map((b) => (
          <li key={b.employer_id} className="py-3 border-b"
              style={{ borderColor: 'var(--color-hairline)', fontSize: '1.15rem' }}>
            <strong>{b.booth}</strong> — {b.name}
            {b.jobs.length > 0 && (
              <span className="text-secondary">
                {' '}({b.jobs.map((j) => j.title).join('; ')})
              </span>
            )}
          </li>
        ))}
      </ul>
    </div>
  )
}
