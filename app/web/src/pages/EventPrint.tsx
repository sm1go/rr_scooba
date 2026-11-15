import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { EventSummary, MyEventData } from '../types'

/** /event/print — "Your plan" (§9.3) in an A4-friendly layout. */
export default function EventPrint() {
  const { t } = useI18n()
  const [my, setMy] = useState<MyEventData | null>(null)
  const [err, setErr] = useState(false)

  useEffect(() => {
    (async () => {
      try {
        const d = await api<{ events: EventSummary[] }>('/api/events')
        const next = d.events.find(
          (e) => e.phase !== 'after' && e.phase !== 'closed')
          ?? d.events[0]
        if (!next) { setErr(true); return }
        setMy(await api<MyEventData>(`/api/events/${next.id}/my`))
      } catch { setErr(true) }
    })()
  }, [])

  if (err) return <p>{t('common.error')}</p>
  if (!my) return <p>{t('common.loading')}</p>
  const ev = my.event
  const meetings = [...my.meetings]
    .sort((a, b) => a.starts_at.localeCompare(b.starts_at))

  return (
    <div className="print-sheet max-w-3xl mx-auto">
      <div className="no-print flex justify-between items-center mb-4">
        <Link to={`/events/${ev.id}`} className="text-secondary">
          {`← ${t('common.back')}`}</Link>
        <button type="button" className="btn btn-primary"
                onClick={() => window.print()}>
          {t('print.print')}
        </button>
      </div>
      <h1 data-page-title tabIndex={-1}>{ev.name}</h1>
      <p className="text-secondary">
        {ev.date} · {ev.venue}{ev.address ? `, ${ev.address}` : ''}
      </p>

      <div className="card p-6 text-center my-5">
        <p className="m-0 text-secondary">{t('event.number')}</p>
        <p className="m-0 font-display"
           style={{ fontSize: '5rem', lineHeight: 1.1 }}>
          {my.visitor_code ?? '—'}
        </p>
        <p className="m-0 mt-2">{t('ev.day.passtext')}</p>
        {my.entry && (
          <p className="m-0 mt-2 font-medium">
            {t('ev.day.entry', {
              t: my.entry, g: my.registration?.time_group ?? '' })}
          </p>
        )}
      </div>

      <h2>{t('ev.step.plan')}</h2>
      <ul className="m-0 p-0 list-none">
        {meetings.map((m) => (
          <li key={m.id} className="py-3 border-b"
              style={{ borderColor: 'var(--color-hairline)',
                       fontSize: '1.15rem' }}>
            <strong>{m.starts_at.slice(11, 16)}</strong>
            {' — '}{m.employer_name}
            {m.booth ? ` (${t('ev.booth')} ${m.booth})` : ''}
            {m.video_url ? ` — ${m.video_url}` : ''}
            {m.first_week && m.first_week.length > 0 && (
              <span className="block text-secondary"
                    style={{ fontSize: '1rem' }}>
                {m.first_week.join('; ')}</span>
            )}
          </li>
        ))}
        {meetings.length === 0 &&
          <li className="py-3">{t('ev.meetings.none')}</li>}
      </ul>
    </div>
  )
}
