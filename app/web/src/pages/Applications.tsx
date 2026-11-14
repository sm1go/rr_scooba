import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Application, EventRecord, EventTalk } from '../types'
import { Chip, ErrorBox, Section } from '../components/ui'
import { fmtDate } from '../lib/format'

const TRACK = ['sent', 'interview', 'offer'] as const
const TONE: Record<string, 'yes' | 'no' | 'wait'> = {
  sent: 'wait', interview: 'wait', offer: 'yes',
  not_selected: 'no', withdrawn: 'no', job_closed: 'no',
}

export default function Applications() {
  const { t } = useI18n()
  const [apps, setApps] = useState<Application[] | null>(null)
  const [talks, setTalks] = useState<EventTalk[]>([])
  const [records, setRecords] = useState<EventRecord[]>([])
  const [err, setErr] = useState('')

  const load = () => {
    api<{ applications: Application[] }>('/api/me/applications')
      .then((r) => setApps(r.applications))
      .catch((e) => setErr(e instanceof ApiError ? e.message : t('common.error')))
    api<{ talks: EventTalk[] }>('/api/me/event-talks')
      .then((r) => setTalks(r.talks)).catch(() => {})
    api<{ records: EventRecord[] }>('/api/me/event-records')
      .then((r) => setRecords(r.records)).catch(() => {})
  }
  useEffect(load, [t])

  const withdraw = async (a: Application) => {
    try {
      await api(`/api/applications/${a.id}/withdraw`, { method: 'POST' })
      load()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  if (!apps) return <p>{t('common.loading')}</p>
  return (
    <div className="max-w-3xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('applications.title')}</h1>
      {err && <ErrorBox>{err}</ErrorBox>}
      {apps.length === 0 && (
        <div className="card p-6 text-center">
          <p>{t('applications.empty')}</p>
          <Link to="/jobs" className="btn btn-primary">{t('nav.jobs')}</Link>
        </div>
      )}
      {apps.map((a) => {
        const trackIdx = TRACK.indexOf(a.status as (typeof TRACK)[number])
        return (
          <article key={a.id} className="card p-5 mb-4">
            <div className="flex justify-between gap-3 flex-wrap">
              <div>
                <Link to={`/jobs/${a.job_id}`} className="no-underline"
                      style={{ color: 'var(--color-ink)' }}>
                  <h2 className="m-0 font-display" style={{ fontSize: '1.25rem' }}>
                    {a.job?.title ?? a.job_id}
                  </h2>
                </Link>
                <p className="m-0 mt-1 text-secondary">
                  {a.job?.employer_name}
                  {' · '}{t('applications.sent')} {fmtDate(a.created_at)}
                  {a.created_by_advisor && ` · ${t('applications.byadvisor')}`}
                </p>
              </div>
              <Chip tone={TONE[a.status] ?? 'wait'}>
                {t(`status.${a.status}` as Key)}
              </Chip>
              {a.queue_position != null && (
                <p className="m-0 mt-2 font-medium">
                  {t('apps.queue', { n: a.queue_position })}
                </p>
              )}
            </div>

            <div className="flex gap-0 mt-4" role="list"
                 aria-label={t('applications.title')}>
              {TRACK.map((s, i) => (
                <div key={s} role="listitem"
                     className="flex-1 text-center text-secondary"
                     style={{ fontSize: '1rem' }}>
                  <div className="mx-auto mb-1 rounded-full" style={{
                    width: 14, height: 14,
                    background: trackIdx >= i
                      ? 'var(--color-ink)' : 'var(--color-hairline)',
                  }} />
                  {t(`status.${s}` as Key)}
                </div>
              ))}
            </div>

            {a.status_note && (
              <p className="text-secondary mt-3">{a.status_note}</p>
            )}
            <p className="text-secondary" style={{ fontSize: '1rem' }}>
              {t('applications.waiting')} {a.days_waiting ?? 0} {t('common.days')}
            </p>

            {(a.status === 'sent' || a.status === 'interview') && (
              <button type="button" className="btn btn-quiet mt-2"
                      onClick={() => withdraw(a)}>
                {t('applications.withdraw')}
              </button>
            )}
          </article>
        )
      })}

      {talks.length > 0 && (
        <Section title={t('apps.eventtalks')}>
          {talks.map((tk) => (
            <article key={tk.id} className="card p-4 mb-3">
              <div className="flex justify-between gap-3 flex-wrap">
                <p className="m-0 font-medium">
                  {t('apps.talked')} {tk.employer_name} — {fmtDate(tk.talked_at)}
                </p>
                <Chip tone={tk.status === 'answered' ? 'yes' : 'wait'}>
                  {tk.status === 'answered' ? t('empevent.answered') : t('empevent.needsanswer')}
                </Chip>
              </div>
              {tk.outcome && (
                <p className="m-0 mt-2">
                  {tk.outcome === 'next_step' ? t('empevent.nextstep') : t('empevent.notnow')}
                </p>
              )}
              {tk.employer_note && (
                <p className="m-0 mt-1 text-secondary">
                  {t('apps.talknote')}: {tk.employer_note}
                </p>
              )}
            </article>
          ))}
        </Section>
      )}

      {records.length > 0 && (
        <Section title={t('ev.after.seen')}>
          {records.map((r, i) => (
            <article key={i} className="card p-4 mb-3">
              <p className="m-0 font-medium">{r.employer} — {fmtDate(r.date)}</p>
              <ul className="m-0 mt-1 ps-5">
                {r.observed.map((o, j) => <li key={j}>{o}</li>)}
              </ul>
            </article>
          ))}
        </Section>
      )}
    </div>
  )
}
