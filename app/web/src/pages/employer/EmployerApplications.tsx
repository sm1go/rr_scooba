import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { Application } from '../../types'
import { Chip, ErrorBox, ErrorState, Field } from '../../components/ui'

const STATUS_TONE: Record<string, 'yes' | 'no' | 'wait'> = {
  sent: 'wait', interview: 'wait', offer: 'yes',
  not_selected: 'no', withdrawn: 'no', job_closed: 'no',
}

export default function EmployerApplications() {
  const { t } = useI18n()
  const [params] = useSearchParams()
  const jobId = params.get('job')
  const [apps, setApps] = useState<Application[] | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const [actErr, setActErr] = useState('')
  const [editing, setEditing] = useState<string | null>(null)
  const [status, setStatus] = useState<'interview' | 'offer' | 'not_selected'>('interview')
  const [note, setNote] = useState('')

  const load = () => {
    setErr(null)
    api<{ applications: Application[] }>(
      `/api/employer/applications${jobId ? `?job_id=${jobId}` : ''}`)
      .then((r) => setApps(r.applications))
      .catch((e) => { setErr(e); setApps([]) })
  }
  useEffect(load, [jobId, t])

  const send = async (a: Application) => {
    try {
      await api(`/api/applications/${a.id}/status`, {
        body: { status, status_note: note },
      })
      setEditing(null); setNote('')
      load()
    } catch (e) {
      setActErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  const groups = useMemo(() => {
    const m = new Map<string, { title: string; items: Application[];
                                openHiring: boolean }>()
    for (const a of apps ?? []) {
      const g = m.get(a.job_id) ?? {
        title: a.job?.title ?? a.job_id, items: [],
        openHiring: (a.job?.commitments ?? []).includes('open_hiring'),
      }
      g.items.push(a)
      m.set(a.job_id, g)
    }
    return [...m.entries()]
  }, [apps])

  if (err && apps !== null) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!apps) return <p>{t('common.loading')}</p>
  return (
    <div className="max-w-4xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('employer.applications')}</h1>
      {actErr && <ErrorBox>{actErr}</ErrorBox>}
      {apps.length === 0 && <p>{t('employer.noapplications')}</p>}
      {groups.map(([jid, g]) => (
        <section key={jid} className="mb-6">
          <h2 className="font-display" style={{ fontSize: '1.3rem' }}>
            <Link to={`/jobs/${jid}`}>{g.title}</Link>
          </h2>
          {g.openHiring && (
            <div className="card p-4 mb-3"
                 style={{ background: 'var(--color-wait-bg)' }}>
              <p className="m-0">{t('employer.openhiringbanner')}</p>
            </div>
          )}
          {g.items.map((a) => (
            <article key={a.id} className="card p-5 mb-3">
              <div className="flex justify-between gap-3 flex-wrap">
                <div>
                  <h3 className="m-0" style={{ fontSize: '1.1rem' }}>{a.name}</h3>
                  <p className="m-0 mt-1 text-secondary">
                    {a.contact_method}: {a.contact_value}
                    {' · '}{a.created_at?.slice(0, 10)}
                    {' · '}{a.days_waiting} {t('common.days')}
                  </p>
                </div>
                <Chip tone={STATUS_TONE[a.status] ?? 'wait'}>
                  {t(`status.${a.status}` as Key)}
                </Chip>
              </div>
              {a.availability_note && (
                <p className="mt-2 mb-0">
                  <strong>{t('apply.availability')}:</strong> {a.availability_note}
                </p>
              )}
              {a.answer && (
                <p className="mt-2 mb-0 whitespace-pre-wrap">
                  <strong>{t('apply.question')}:</strong> {a.answer}
                </p>
              )}
              {a.shared_needs.length > 0 && (
                <p className="mt-2 mb-0">
                  <strong>{t('apply.share')}:</strong>{' '}
                  {a.shared_needs.map((k) => t(`cond.${k}` as Key)).join(', ')}
                </p>
              )}
              {a.queue_position != null && (
                <p className="mt-2 mb-0 font-medium">
                  {t('employer.queue', { n: a.queue_position })}
                </p>
              )}
              {a.meets_must_haves && (
                <p className="mt-2 mb-0">{t('employer.meetsmust')}</p>
              )}
              {a.wants_tryout && (
                <p className="mt-2 mb-0">{t('employer.wantstryout')}</p>
              )}
              {a.contract_eligible && (
                <p className="mt-2 mb-0">{t('employer.contracteligible')}</p>
              )}
              {a.shared_credentials?.length > 0 && (
                <p className="mt-2 mb-0">
                  {t('employer.creds')}:{' '}
                  {a.shared_credentials.map((c) => c.label).join(', ')}
                </p>
              )}
              {a.shared_event_records?.length > 0 && (
                <p className="mt-2 mb-0">
                  {t('employer.eventrecords')}:{' '}
                  {a.shared_event_records.map((r) =>
                    `${r.employer} (${r.date})`).join('; ')}
                </p>
              )}
              {a.meet_at_event && (
                <p className="mt-2 mb-0">{t('apply.event')}</p>
              )}
              {a.status_note && (
                <p className="mt-2 mb-0 text-secondary">{a.status_note}</p>
              )}

              {(a.status === 'sent' || a.status === 'interview') && (
                editing === a.id ? (
                  <div className="mt-3 card p-4">
                    <Field label={t('employer.setstatus')} id={`st-${a.id}`}>
                      <div className="flex gap-2 flex-wrap">
                        {(['interview', 'offer', 'not_selected'] as const).map((s) => (
                          <label key={s} className="flex items-center gap-2"
                                 style={{ minHeight: 48 }}>
                            <input type="radio" name={`st-${a.id}`}
                                   checked={status === s}
                                   onChange={() => setStatus(s)} />
                            {t(`status.${s}` as Key)}
                          </label>
                        ))}
                      </div>
                    </Field>
                    <Field label={t('employer.statusnote')} id={`note-${a.id}`}>
                      <textarea id={`note-${a.id}`} value={note} required
                                onChange={(e) => setNote(e.target.value)} />
                    </Field>
                    <div className="flex gap-2">
                      <button type="button" className="btn btn-secondary"
                              onClick={() => setEditing(null)}>
                        {t('common.back')}
                      </button>
                      <button type="button" className="btn btn-primary"
                              disabled={!note.trim()}
                              onClick={() => send(a)}>
                        {t('common.send')}
                      </button>
                    </div>
                  </div>
                ) : (
                  <button type="button" className="btn btn-secondary mt-3"
                          onClick={() => { setEditing(a.id); setStatus('interview') }}>
                    {t('employer.setstatus')}
                  </button>
                )
              )}
            </article>
          ))}
        </section>
      ))}
    </div>
  )
}
