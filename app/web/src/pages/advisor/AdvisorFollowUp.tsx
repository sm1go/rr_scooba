import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { Overview } from '../../types'
import { Chip, ErrorState, Section } from '../../components/ui'
import { fmtDate } from '../../lib/format'

export default function AdvisorFollowUp() {
  const { t, lang } = useI18n()
  const [ov, setOv] = useState<Overview | null>(null)
  const [events, setEvents] = useState<{ id: number; actor: string; action: string; detail: string; created_at: string }[]>([])
  const [err, setErr] = useState<unknown>(null)

  const load = () => {
    setErr(null)
    api<Overview>('/api/advisor/overview').then(setOv)
      .catch((e) => setErr(e))
    api<{ events: typeof events }>('/api/audit?limit=50')
      .then((r) => setEvents(r.events)).catch(() => {})
  }
  useEffect(load, [t])

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!ov) return <p>{t('common.loading')}</p>
  return (
    <div className="max-w-4xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('advisor.followup')}</h1>

      <div className="grid gap-3 md:grid-cols-3 mb-5">
        <div className="card p-4 text-center">
          <div className="font-display" style={{ fontSize: '2rem' }}>{ov.open_jobs}</div>
          <div className="text-secondary">{t('advisor.openjobs')}</div>
        </div>
        <div className="card p-4 text-center">
          <div className="font-display" style={{ fontSize: '2rem' }}>{ov.stale_jobs.length}</div>
          <div className="text-secondary">{t('advisor.stalejobs')}</div>
        </div>
        <div className="card p-4 text-center">
          <div className="font-display" style={{ fontSize: '2rem' }}>{ov.new_help_requests}</div>
          <div className="text-secondary">{t('advisor.requests')}</div>
        </div>
      </div>

      <Section title={t('advisor.stalejobs')}>
        {ov.stale_jobs.length === 0 && <p className="text-secondary">{t('advisor.empty')}</p>}
        {ov.stale_jobs.map((j) => (
          <div key={j.id} className="flex justify-between gap-3 py-2 border-b"
               style={{ borderColor: 'var(--color-hairline)' }}>
            <div>
              <Link to={`/jobs/${j.id}`}>{j.title}</Link>
              <span className="text-secondary"> — {j.employer_name}</span>
            </div>
            <Chip tone="wait">
              {j.confirmed_days_ago} {t('common.days')}
            </Chip>
          </div>
        ))}
      </Section>

      <Section title={t('advisor.waiting')}>
        {ov.waiting_over_7_days.length === 0 && (
          <p className="text-secondary">{t('advisor.empty')}</p>
        )}
        {ov.waiting_over_7_days.map((a) => (
          <div key={a.id} className="py-2 border-b"
               style={{ borderColor: 'var(--color-hairline)' }}>
            <Link to={`/jobs/${a.job_id}`}>{a.job_title}</Link>
            <span className="text-secondary">
              {' — '}{a.applicant_name} · {t(`status.${a.status}` as Key)}
              {' · '}{a.days_waiting} {t('common.days')}
            </span>
            {a.employer && (
              <p className="m-0 text-secondary" style={{ fontSize: '1rem' }}>
                {a.employer.name} · {a.employer.contact_email} · {a.employer.contact_phone}
              </p>
            )}
          </div>
        ))}
      </Section>

      {ov.event_talks_unanswered.length > 0 && (
        <Section title={t('advisor.followup.talks')}>
          {ov.event_talks_unanswered.map((tk) => (
            <div key={tk.id} className="py-2 border-b"
                 style={{ borderColor: 'var(--color-hairline)' }}>
              <strong>{tk.person_name}</strong>
              <span className="text-secondary">
                {' — '}{tk.employer_name} · {tk.days_waiting} {t('common.days')}
              </span>
              {tk.employer && (
                <p className="m-0 text-secondary" style={{ fontSize: '1rem' }}>
                  {tk.employer.contact_name} · {tk.employer.contact_email} · {tk.employer.contact_phone}
                </p>
              )}
            </div>
          ))}
        </Section>
      )}

      <Section title={t('advisor.activity')}>
        <ul className="m-0 p-0 list-none">
          {events.map((e) => (
            <li key={e.id} className="py-1 text-secondary"
                style={{ fontSize: '1rem' }}>
              {fmtDate(e.created_at, lang)} — {e.action} {e.detail}
            </li>
          ))}
        </ul>
      </Section>
    </div>
  )
}
