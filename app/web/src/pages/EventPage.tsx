import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { EventInfo, EventPlan } from '../types'
import { ErrorState, Section } from '../components/ui'

/** /event — the recruitment event: booth plan, employer list, My plan. */
export default function EventPage() {
  const { t } = useI18n()
  const { user } = useAuth()
  const [info, setInfo] = useState<EventInfo | null>(null)
  const [plan, setPlan] = useState<EventPlan | null>(null)
  const [err, setErr] = useState<unknown>(null)

  const load = () => {
    setErr(null)
    api<EventInfo>('/api/event').then(setInfo).catch(setErr)
    if (user?.role === 'resident') {
      api<EventPlan>('/api/me/event-plan').then(setPlan).catch(() => setPlan(null))
    } else setPlan(null)
  }
  useEffect(load, [user])

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!info) return <p>{t('common.loading')}</p>
  if (!info.event) {
    return (
      <div className="max-w-3xl mx-auto">
        <h1 data-page-title tabIndex={-1}>{t('event.title')}</h1>
        <p className="card p-5">{t('event.empty')}</p>
      </div>
    )
  }
  const ev = info.event
  const inPlan = new Set(plan?.booths.map((b) => b.employer_id) ?? [])

  const setPlanItem = async (employerId: string, add: boolean) => {
    try {
      const r = await api<EventPlan>(`/api/me/event-plan/${employerId}`,
        { method: add ? 'PUT' : 'DELETE' })
      setPlan(r)
    } catch { /* sign-in guard handles */ }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{ev.name}</h1>
      <p className="text-secondary" style={{ fontSize: '1.1rem' }}>
        {ev.date} · {ev.venue}
      </p>
      <p className="card p-4 font-medium">{ev.advisor_note || t('event.advisor')}</p>

      {user?.role === 'resident' && plan?.code && (
        <Section title={t('event.myplan')}>
          <div className="card p-5 mb-3 text-center">
            <p className="m-0 text-secondary">{t('event.number')}</p>
            <p className="m-0 font-display" style={{ fontSize: '4rem', lineHeight: 1.1 }}
               aria-label={`${t('event.number')} ${plan.code.split('').join(' ')}`}>
              {plan.code}
            </p>
            <p className="m-0 mt-2 text-secondary">{t('event.numberwhy')}</p>
          </div>
          {plan.booths.length === 0 && (
            <p className="text-secondary">{t('event.planempty')}</p>
          )}
          <ol className="m-0 p-0 list-none">
            {plan.booths.map((b) => (
              <li key={b.employer_id} className="card p-4 mb-2 flex justify-between gap-3 flex-wrap">
                <div>
                  <strong>{b.booth}</strong> — {b.name}
                  <ul className="m-0 mt-1 pl-5 text-secondary">
                    {b.jobs.map((j) => (
                      <li key={j.id}><Link to={`/jobs/${j.id}`}>{j.title}</Link></li>
                    ))}
                  </ul>
                </div>
                <button type="button" className="btn btn-quiet"
                        onClick={() => setPlanItem(b.employer_id, false)}>
                  {t('event.remove')}
                </button>
              </li>
            ))}
          </ol>
          {plan.booths.length > 0 && (
            <Link to="/event/print" className="btn btn-primary mt-2">
              {t('event.print')}
            </Link>
          )}
        </Section>
      )}
      {!user && (
        <p className="card p-4">
          <Link to={`/sign-in?back=${encodeURIComponent('/event')}`}>{t('event.signin')}</Link>
        </p>
      )}

      <Section title={t('event.boothplan')}>
        <div className="booth-grid" role="list">
          {info.employers.map((e) => (
            <div key={e.id} role="listitem" className="booth-cell card p-4">
              <div className="font-display" style={{ fontSize: '1.4rem' }}>{e.booth}</div>
              <div>{e.name}</div>
            </div>
          ))}
        </div>
      </Section>

      <Section title={t('event.openjobs')}>
        {info.employers.map((e) => (
          <div key={e.id} className="card p-4 mb-3">
            <div className="flex justify-between gap-3 flex-wrap">
              <div>
                <strong>{e.booth}</strong> — {e.name}
              </div>
              {user?.role === 'resident' && (
                inPlan.has(e.id) ? (
                  <button type="button" className="btn btn-quiet"
                          onClick={() => setPlanItem(e.id, false)}>
                    {t('event.inplan')} ✓
                  </button>
                ) : (
                  <button type="button" className="btn btn-secondary"
                          onClick={() => setPlanItem(e.id, true)}>
                    {t('event.addplan')}
                  </button>
                )
              )}
            </div>
            <ul className="m-0 mt-2 pl-5">
              {e.jobs.map((j) => (
                <li key={j.id}><Link to={`/jobs/${j.id}`}>{j.title}</Link></li>
              ))}
            </ul>
          </div>
        ))}
      </Section>
    </div>
  )
}
