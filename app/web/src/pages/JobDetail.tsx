import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Catalog, Job } from '../types'
import { Chip, ErrorState, Section } from '../components/ui'
import { labelText } from '../components/JobRow'
import JobMap from '../components/JobMap'
import ConditionTable from '../components/ConditionTable'
import ListenButton from '../components/ListenButton'
import { daysAgoText, districtName, hoursLine, payLine, shiftsLine } from '../lib/format'

export default function JobDetail() {
  const { id } = useParams()
  const { t } = useI18n()
  const { user } = useAuth()
  const [job, setJob] = useState<Job | null>(null)
  const [cat, setCat] = useState<Catalog | null>(null)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<unknown>(null)

  const load = () => {
    setError(null)
    api<Job>(`/api/jobs/${id}`).then(setJob).catch((e) => setError(e))
  }
  useEffect(() => {
    load()
    api<Catalog>('/api/catalog').then(setCat).catch(() => {})
    if (user?.role === 'resident') {
      api<{ jobs: { id: string }[] }>('/api/me/saved')
        .then((r) => setSaved(r.jobs.some((j) => j.id === id)))
        .catch(() => {})
    }
  }, [id, user])

  if (error) {
    return (
      <ErrorState err={error} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!job) return <p>{t('common.loading')}</p>

  const listenText = [
    job.title, job.employer?.name, payLine(job, t),
    hoursLine(job, t), shiftsLine(job, t),
    ...(job.duties ?? []),
  ].join('. ')

  const toggleSave = async () => {
    if (!user) return
    if (saved) {
      await api(`/api/me/saved/${job.id}`, { method: 'DELETE' })
      setSaved(false)
    } else {
      await api(`/api/me/saved/${job.id}`, { method: 'PUT' })
      setSaved(true)
    }
  }

  return (
    <div className="pb-28">
      <Link to="/" className="text-secondary">{`← ${t('common.back')}`}</Link>
      <h1 data-page-title tabIndex={-1} className="mt-2">{job.title}</h1>
      <p className="text-secondary" style={{ fontSize: '1.1rem' }}>
        {job.employer?.name}
        {cat && ` · ${districtName(job.district, cat.districts)}`}
        {job.distance_km != null && ` · ${job.distance_km} km`}
      </p>

      {job.labels.length > 0 && (
        <div className="mb-5">
          {job.labels.map((l) => (
            <details key={l.id} className="card p-3 mb-2">
              <summary className="cursor-pointer font-medium">
                <Chip tone="yes">{labelText(l.id, t)}</Chip>
                <span className="text-secondary ml-2" style={{ fontSize: '1rem' }}>
                  {t('job.why')}
                </span>
              </summary>
              <p className="m-0 mt-2 text-secondary">{l.why}</p>
            </details>
          ))}
        </div>
      )}

      <Section title={t('job.whatyoudo')}>
        <ul className="m-0 pl-5">
          {job.duties.map((d, i) => <li key={i} className="mb-2">{d}</li>)}
        </ul>
      </Section>

      <Section title={t('job.where')}>
        <p className="m-0 mb-2">{job.address}</p>
        <p className="m-0 mb-3 text-secondary">
          {job.work_mode === 'remote' ? t('common.remote')
            : job.work_mode === 'hybrid' ? t('common.hybrid') : t('common.onsite')}
          {job.distance_km != null && ` · ${job.distance_km} km`}
        </p>
        {job.lat != null && job.lon != null && job.work_mode !== 'remote' && (
          <div className="card overflow-hidden">
            <JobMap jobs={[job]} height={220} />
          </div>
        )}
      </Section>

      <Section title={t('job.pay')}>
        <p className="m-0" style={{ fontSize: '1.15rem' }}>{payLine(job, t)}</p>
      </Section>

      <Section title={t('job.when')}>
        <p className="m-0">{shiftsLine(job, t)}</p>
        {(job.hours_min != null || job.hours_max != null) && (
          <p className="m-0 mt-1">{hoursLine(job, t)}</p>
        )}
        {job.schedule_flexible ? (
          <p className="m-0 mt-1 text-secondary">{t('common.flexible')}</p>
        ) : null}
      </Section>

      <Section title={t('job.contract')}>
        <p className="m-0">
          {job.contract ? t(`contract.${job.contract}` as Key) : t('common.unknown')}
          {job.positions > 1 && ` · ${job.positions} ${t('common.positions')}`}
        </p>
      </Section>

      <Section title={t('job.whatyouneed')}>
        <p className="m-0">
          {job.experience ? t(`experience.${job.experience}` as Key) : t('common.unknown')}
        </p>
        {job.experience_note && <p className="text-secondary mt-1">{job.experience_note}</p>}
        {job.qualifications.length > 0 && (
          <ul className="pl-5 mt-2 mb-2">
            {job.qualifications.map((q, i) => <li key={i}>{q}</li>)}
          </ul>
        )}
        {job.languages.length > 0 && (
          <ul className="pl-5 mt-2 mb-0">
            {job.languages.map((l, i) => (
              <li key={i}>{l.language} {l.level}{l.task ? ` — ${l.task}` : ''}</li>
            ))}
          </ul>
        )}
      </Section>

      {job.onboarding && (
        <Section title={t('job.training')}>
          <p className="m-0">{job.onboarding}</p>
        </Section>
      )}

      <div id="job-conditions" />
      <Section title={t('job.conditions')}>
        <ConditionTable job={job} jobId={job.id} />
      </Section>

      {job.event && (
        <Section title={t('job.atevent')}>
          <p className="m-0">{job.event.name} — {job.event.date}</p>
          <p className="m-0 text-secondary">{job.event.venue} · {t('job.booth')} {job.event.booth}</p>
          <p className="m-0 mt-1">{t('job.eventnote')}</p>
        </Section>
      )}

      <p className="text-secondary">
        {t('job.source')}{' '}
        {job.source === 'advisor' ? t('job.source.advisor') : t('job.source.employer')}
        {' · '}{job.stale
          ? t('jobs.notconfirmed')
          : daysAgoText(job.confirmed_days_ago, t)}
      </p>

      <div className="fixed bottom-[70px] md:bottom-0 left-0 right-0 z-30 border-t p-3"
           style={{ background: 'var(--color-card)', borderColor: 'var(--color-hairline)' }}>
        <div className="max-w-6xl mx-auto px-2 flex gap-2 flex-wrap">
          <Link to={`/jobs/${job.id}/apply`} className="btn btn-primary flex-1">
            {t('common.apply')}
          </Link>
          <Link to={`/help?job=${job.id}`} className="btn btn-secondary flex-1">
            {t('nav.help')}
          </Link>
          {user?.role === 'resident' && (
            <button type="button" className="btn btn-quiet" onClick={toggleSave}
                    aria-pressed={saved}>
              {saved ? t('common.saved') : t('common.save')}
            </button>
          )}
          <ListenButton text={listenText} />
        </div>
      </div>
    </div>
  )
}
