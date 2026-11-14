import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { Job } from '../../types'
import { Chip, ErrorBox, ErrorState } from '../../components/ui'
import { daysAgoText, fmtDate } from '../../lib/format'

export default function EmployerJobs() {
  const { t, lang } = useI18n()
  const [jobs, setJobs] = useState<Job[] | null>(null)
  const [contracts, setContracts] = useState<{ id: string; title: string;
    due: string; hires_done: number; hires_required: number }[]>([])
  const [err, setErr] = useState<unknown>(null)

  const load = () => {
    setErr(null)
    api<{ jobs: Job[] }>('/api/employer/jobs')
      .then((r) => setJobs(r.jobs))
      .catch((e) => { setErr(e); setJobs([]) })
    api<{ contracts: typeof contracts }>('/api/employer/contracts')
      .then((r) => setContracts(r.contracts)).catch(() => undefined)
  }
  useEffect(load, [t])

  if (err && jobs !== null) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }

  const act = async (id: string, action: 'confirm' | 'close') => {
    try {
      await api(`/api/jobs/${id}/${action}`, { method: 'POST' })
      load()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  if (!jobs) return <p>{t('common.loading')}</p>
  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-baseline justify-between flex-wrap gap-3">
        <h1 data-page-title tabIndex={-1}>{t('employer.jobs')}</h1>
        <Link to="/employer/jobs/new" className="btn btn-primary">
          {t('employer.addjob')}
        </Link>
      </div>
      {contracts.map((c) => (
        <div key={c.id} className="card p-4 mb-3" style={{ background: 'var(--color-yes-bg)' }}>
          <p className="m-0">
            {t('employer.contractbanner', { title: c.title, n: c.hires_done,
                                           req: c.hires_required, due: fmtDate(c.due, lang) })}
          </p>
        </div>
      ))}
      {err != null && jobs.length > 0 && <ErrorBox>{String(err)}</ErrorBox>}
      {jobs.length === 0 && <p>{t('employer.empty')}</p>}
      {jobs.map((j) => (
        <article key={j.id} className="card p-5 mb-3">
          <div className="flex justify-between gap-3 flex-wrap">
            <div>
              <h2 className="m-0 font-display" style={{ fontSize: '1.2rem' }}>
                {j.title}
              </h2>
              <p className="m-0 mt-1 text-secondary">
                {j.positions} {t('employer.positions')}
                {' · '}{j.applications_count ?? 0} {t('employer.applications')}
                {' · '}
                {j.status === 'open'
                  ? (j.stale ? t('jobs.notconfirmed')
                      : daysAgoText(j.confirmed_days_ago, t))
                  : j.status === 'draft' ? t('employer.status.draft')
                    : t('employer.status.closed')}
              </p>
            </div>
            <Chip tone={j.status === 'open' ? 'yes'
              : j.status === 'draft' ? 'wait' : 'no'}>
              {j.status === 'open' ? t('employer.status.open')
                : j.status === 'draft' ? t('employer.status.draft')
                  : t('employer.status.closed')}
            </Chip>
          </div>
          <div className="flex gap-2 mt-3 flex-wrap">
            {j.status === 'open' && (
              <button type="button" className="btn btn-secondary"
                      onClick={() => act(j.id, 'confirm')}>
                {t('employer.confirm')}
              </button>
            )}
            {j.status !== 'closed' && (
              <Link to={`/employer/jobs/${j.id}`} className="btn btn-secondary">
                {t('common.edit')}
              </Link>
            )}
            {j.status === 'open' && (
              <button type="button" className="btn btn-quiet"
                      onClick={() => act(j.id, 'close')}>
                {t('employer.close')}
              </button>
            )}
            <Link to={`/employer/applications?job=${j.id}`}
                  className="btn btn-quiet">
              {t('employer.applications')}
            </Link>
          </div>
        </article>
      ))}
    </div>
  )
}
