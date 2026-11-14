import { useEffect, useState } from 'react'
import { Link, useParams, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useConfig } from '../lib/config'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Catalog, Commute, Job, SimplerSections, SupportCatalogue } from '../types'
import { Chip, ErrorState, Section } from '../components/ui'
import { labelText } from '../components/JobRow'
import JobMap from '../components/JobMap'
import ConditionTable from '../components/ConditionTable'
import ListenButton from '../components/ListenButton'
import {
  conditionState, daysAgoText, districtName, helpLink, hoursLine, payLine, shiftsLine,
} from '../lib/format'
import { commuteLine, legText } from '../lib/commute'
import { employerProgramsFor } from '../lib/support'

export default function JobDetail() {
  const { id } = useParams()
  const { t, lang } = useI18n()
  const { user } = useAuth()
  const cfg = useConfig()
  const [job, setJob] = useState<Job | null>(null)
  const [cat, setCat] = useState<Catalog | null>(null)
  const [saved, setSaved] = useState(false)
  const [error, setError] = useState<unknown>(null)
  const [commute, setCommute] = useState<Commute | null>(null)
  const [simpler, setSimpler] = useState<SimplerSections | null>(null)
  const [simplerErr, setSimplerErr] = useState('')
  const [simplerBusy, setSimplerBusy] = useState(false)
  const [maySupport, setMaySupport] = useState(false)

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

  // Commute (§5): works signed out. Origin = ?district= from the list
  // filter, else the resident's profile district.
  const [search] = useSearchParams()
  const [originId, setOriginId] = useState<string | null>(null)
  useEffect(() => {
    setCommute(null)
    setOriginId(null)
    if (!cfg.commute || !job || job.work_mode === 'remote') return
    const fromUrl = search.get('district')
    const fetchFor = (district: string) => {
      setOriginId(district)
      api<Commute>(`/api/commute?job_id=${job.id}&district=${district}`)
        .then(setCommute).catch(() => undefined)
    }
    if (fromUrl) { fetchFor(fromUrl); return }
    if (user?.role !== 'resident') return
    api<{ district: string | null }>('/api/me/profile')
      .then((p) => { if (p.district) fetchFor(p.district) })
      .catch(() => undefined)
  }, [cfg.commute, job, user, search])

  // Quiet support line — employer-side programmes that fit this job (§7).
  useEffect(() => {
    if (!job) return
    api<SupportCatalogue>('/api/support')
      .then((c) => setMaySupport(employerProgramsFor(job, c.programs).length > 0))
      .catch(() => undefined)
  }, [job])

  const simplify = async () => {
    setSimplerBusy(true); setSimplerErr('')
    try {
      const r = await api<{ sections: SimplerSections }>('/api/ai/simplify', {
        body: { job_id: job!.id, language: lang },
      })
      setSimpler(r.sections)
    } catch (e) {
      setSimplerErr(e instanceof ApiError ? e.message : t('job.simpler.fail'))
    } finally { setSimplerBusy(false) }
  }

  if (error) {
    return (
      <ErrorState err={error} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!job) return <p>{t('common.loading')}</p>

  const originName = cat && originId ? districtName(originId, cat.districts) : ''
  const unknownKeys = job.conditions.filter((c) => c.value === 'unknown').map((c) => c.key)
  const listenText = [
    job.title, job.employer?.name, payLine(job, t),
    hoursLine(job, t), shiftsLine(job, t),
    commute && originName ? commuteLine(commute, originName, t) : '',
    t('job.conditions'),
    ...job.conditions.map((c) => `${t(`cond.${c.key}` as Key)}: ${conditionState(c, t)}`),
    `${t('job.lifting')}: ${job.lifting || t('common.unknown')}`,
    ...(job.duties ?? []),
  ].filter(Boolean).join('. ')

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
      {job.nearest_station && (
        <p className="text-secondary">
          {t('jobs.station.line', {
            d: job.nearest_station.distance_m,
            name: job.nearest_station.name,
            kind: t(`station.${job.nearest_station.mode}` as Key),
          })}
        </p>
      )}
      {commute && cat && originId && (
        <p className="text-secondary">
          {commuteLine(commute, districtName(originId, cat.districts), t)}
          {' '}
          <span>({t('commute.arriving', { t: commute.arrive_by.slice(11, 16) })})</span>
        </p>
      )}
      {commute && cat && originId && (
        <details className="mt-1">
          <summary className="cursor-pointer text-secondary">
            {t('commute.legs')}
          </summary>
          <ol className="m-0 mt-1 ps-5 text-secondary">
            {commute.legs.map((l, i) => (
              <li key={i}>{legText(l, districtName(originId, cat.districts), t)}</li>
            ))}
          </ol>
        </details>
      )}

      <div className="flex gap-2 items-center flex-wrap mb-4">
        {simpler ? (
          <button type="button" className="btn btn-quiet" onClick={() => setSimpler(null)}>
            {t('job.simpler.original')}
          </button>
        ) : (
          <button type="button" className="btn btn-quiet" disabled={simplerBusy || !cfg.ai}
                  onClick={simplify}>
            {t('job.simpler')}
          </button>
        )}
        {!cfg.ai && <span className="text-secondary">{t('ai.off')}</span>}
        {simplerErr && <span className="text-secondary">{simplerErr}</span>}
        <Link to={`/jobs/${job.id}/print`} className="ms-auto underline text-secondary"
              style={{ fontSize: '1rem', padding: '10px 4px' }}>
          {t('job.print')}
        </Link>
      </div>
      {simpler && (
        <p className="card p-3 mb-4 text-secondary">{t('job.simpler.machine')}</p>
      )}

      {job.labels.length > 0 && (
        <div className="mb-5">
          {job.labels.map((l) => (
            <details key={l.id} className="card p-3 mb-2">
              <summary className="cursor-pointer font-medium">
                <Chip tone="yes">{labelText(l.id, t)}</Chip>
                <span className="text-secondary ms-2" style={{ fontSize: '1rem' }}>
                  {t('job.why')}
                </span>
              </summary>
              <p className="m-0 mt-2 text-secondary">{l.why}</p>
            </details>
          ))}
        </div>
      )}

      <div id="job-conditions" />
      <Section title={t('job.conditions')}>
        {unknownKeys.length > 0 && (
          <div className="card p-4 mb-3 flex flex-wrap items-center justify-between gap-3"
               style={{ background: 'var(--color-wait-bg)' }}>
            <p className="m-0 font-medium">{t('job.unknownbanner', { n: unknownKeys.length })}</p>
            <Link to={helpLink(job.id, unknownKeys)} className="btn btn-secondary">
              {t('job.unknownask')}
            </Link>
          </div>
        )}
        <ConditionTable job={job} jobId={job.id} />
      </Section>

      <Section title={t('job.whatyoudo')}>
        <ul className="m-0 ps-5">
          {(simpler?.duties ?? job.duties).map((d, i) => <li key={i} className="mb-2">{d}</li>)}
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
        {(simpler?.experience_note ?? job.experience_note) && (
          <p className="text-secondary mt-1">{simpler?.experience_note ?? job.experience_note}</p>
        )}
        {(simpler?.qualifications ?? job.qualifications).length > 0 && (
          <ul className="ps-5 mt-2 mb-2">
            {(simpler?.qualifications ?? job.qualifications).map((q, i) => <li key={i}>{q}</li>)}
          </ul>
        )}
        {job.languages.length > 0 && (
          <ul className="ps-5 mt-2 mb-0">
            {job.languages.map((l, i) => (
              <li key={i}>{l.language} {l.level}
                {(simpler?.language_tasks?.[i] ?? l.task)
                  ? ` — ${simpler?.language_tasks?.[i] ?? l.task}` : ''}
              </li>
            ))}
          </ul>
        )}
      </Section>

      {(simpler?.onboarding ?? job.onboarding) && (
        <Section title={t('job.training')}>
          <p className="m-0">{simpler?.onboarding ?? job.onboarding}</p>
        </Section>
      )}

      {job.event && (
        <Section title={t('job.atevent')}>
          <p className="m-0">{job.event.name} — {job.event.date}</p>
          <p className="m-0 text-secondary">{job.event.venue} · {t('job.booth')} {job.event.booth}</p>
          <p className="m-0 mt-1">{t('job.eventnote')}</p>
        </Section>
      )}

      {maySupport && (
        <p className="text-secondary">
          {t('job.maysupport')} <Link to="/support">{t('job.seesupport')}</Link>
        </p>
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
