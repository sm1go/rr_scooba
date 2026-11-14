import type { ReactNode } from 'react'
import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { Bookmark, Clock, UserCheck } from 'lucide-react'
import type { Condition, Job } from '../types'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import { Chip } from './ui'
import { conditionState, daysAgoText, helpLink, hoursLine, payLine, shiftGroups } from '../lib/format'
import { commuteLine, getCommute } from '../lib/commute'
import { useConfig } from '../lib/config'
import { useA11y } from '../lib/a11y'

const LABEL_KEY = {
  students: 'label.students', retirement: 'label.retirement',
  first_job: 'label.first_job', side_job: 'label.side_job',
  part_time: 'label.part_time', access_info: 'label.access_info',
  near_station: 'label.near_station',
} as const

export function labelText(id: string, t: (k: Key) => string) {
  const k = LABEL_KEY[id as keyof typeof LABEL_KEY]
  return k ? t(k) : id
}

/** "6 of 10 workplace facts known · 3 checked by an advisor", the
    person's own needs first, and a way to ask about the unknown ones. */
export function FactsLine({ job, needs = [] }: { job: Job; needs?: string[] }) {
  const { t } = useI18n()
  const conds = job.conditions ?? []
  const known = conds.filter((c) => c.value !== 'unknown')
  const advisor = known.filter((c) => c.source === 'advisor').length
  const unknown = conds.filter((c) => c.value === 'unknown').map((c) => c.key)
  const mine = needs.map((k) => conds.find((c) => c.key === k))
    .filter((c): c is Condition => !!c)
  return (
    <div className="mt-2">
      {mine.length > 0 && (
        <ul className="list-none p-0 m-0 mb-2 flex flex-wrap gap-2">
          {mine.map((c) => (
            <li key={c.key}>
              <Chip tone={c.value === 'yes' ? 'yes' : c.value === 'no' ? 'no' : 'wait'}>
                {t(`cond.${c.key}` as Key)}: {conditionState(c, t)}
              </Chip>
            </li>
          ))}
        </ul>
      )}
      <p className="m-0 flex items-start gap-2">
        <UserCheck size={20} aria-hidden="true" className="shrink-0 mt-1" />
        <span>
          {t('jobs.facts.known', { n: known.length, total: conds.length })}
          {' · '}
          {advisor ? t('jobs.facts.advisor', { n: advisor }) : t('jobs.facts.noadvisor')}
          {unknown.length > 0 && (
            <>
              {' · '}
              <Link to={helpLink(job.id, unknown)} className="relative z-[1]">
                {t('jobs.facts.unknown', { n: unknown.length })}
              </Link>
            </>
          )}
        </span>
      </p>
    </div>
  )
}

/** One job row. The title link is the one target and stretches over the
    card; Save / Show on map / actions sit above it. */
export default function JobRow({
  job, selected, onShowOnMap, districtName, saved, onToggleSave, actions,
  originDistrict, originName, needs,
}: {
  job: Job
  selected?: boolean
  onShowOnMap?: (id: string) => void
  districtName?: string
  saved?: boolean
  onToggleSave?: (j: Job) => void
  actions?: ReactNode
  /** Where the trip starts (§5): id for the API, name for the line. */
  originDistrict?: string
  originName?: string
  /** The person's selected needs, shown first on the facts line. */
  needs?: string[]
}) {
  const { t } = useI18n()
  const cfg = useConfig()
  const calm = useA11y().settings.easierReading
  const ref = useRef<HTMLElement>(null)
  const [commute, setCommute] = useState(job.commute ?? null)
  const [asked, setAsked] = useState(job.commute !== undefined)
  const url = `/jobs/${job.id}${originDistrict ? `?district=${originDistrict}` : ''}`
  const shown = job.labels.slice(0, 3)

  // fetch the commute lazily when the row scrolls into view (§5);
  // max 4 requests at a time, cached per job+district
  useEffect(() => {
    if (calm || !cfg.commute || !originDistrict || asked || job.lat == null
        || job.work_mode === 'remote')
      return
    const el = ref.current
    if (!el || typeof IntersectionObserver === 'undefined') {
      getCommute(job.id, originDistrict)
        .then((c) => { setCommute(c); setAsked(true) })
      return
    }
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) {
        io.disconnect()
        getCommute(job.id, originDistrict)
          .then((c) => { setCommute(c); setAsked(true) })
      }
    }, { rootMargin: '250px' })
    io.observe(el)
    return () => io.disconnect()
  }, [calm, cfg.commute, originDistrict, asked, job])

  const saveBtn = onToggleSave && (
    <button type="button" className="btn btn-quiet relative z-[1]"
            style={{ minHeight: 44, padding: '6px 12px' }}
            aria-pressed={saved}
            aria-label={`${saved ? t('common.saved') : t('common.save')}: ${job.title}`}
            onClick={() => onToggleSave(job)}>
      <Bookmark size={20} fill={saved ? 'currentColor' : 'none'} aria-hidden="true" />
    </button>
  )
  const title = (
    <Link to={url} className="no-underline after:absolute after:inset-0 after:rounded-[inherit]"
          style={{ color: 'var(--color-ink)' }}>
      <h3 className="m-0 font-display" style={{ fontSize: '1.25rem' }}>{job.title}</h3>
    </Link>
  )
  const outline = selected ? { outline: '3px solid var(--color-yes)' } : undefined

  if (calm) {
    return (
      <article ref={ref} id={`job-row-${job.id}`} className="card p-5 mb-3 relative"
               style={outline} aria-current={selected || undefined}>
        <div className="flex justify-between gap-3">
          <div className="min-w-0">
            {title}
            <p className="m-0 mt-1">{job.employer?.name}</p>
            <p className="m-0 mt-1">{payLine(job, t)}</p>
            {hoursLine(job, t) && <p className="m-0 mt-1">{hoursLine(job, t)}</p>}
          </div>
          {saveBtn && <div className="shrink-0">{saveBtn}</div>}
        </div>
        <FactsLine job={job} needs={needs} />
        {actions && <div className="relative z-[1]">{actions}</div>}
      </article>
    )
  }

  return (
    <article ref={ref} id={`job-row-${job.id}`} className="card p-5 mb-3 relative"
             style={outline} aria-current={selected || undefined}>
      <div className="flex flex-wrap justify-between gap-3">
        <div className="min-w-0 flex-1" style={{ minWidth: 'min(100%, 340px)' }}>
          {title}
          <p className="m-0 mt-1 text-secondary">
            {job.employer?.name} · {districtName ?? job.district}
            {job.distance_km != null && ` · ${job.distance_km} km`}
          </p>
          <p className="m-0 mt-2 font-medium" style={{ fontSize: '1.1rem' }}>
            {[payLine(job, t), hoursLine(job, t)].filter(Boolean).join(' · ')}
          </p>
          {shiftGroups(job, t).length > 0 && (
            <div className="m-0 mt-1 flex items-start gap-2">
              <Clock size={18} aria-hidden="true" className="shrink-0 mt-1" />
              <ul className="list-none p-0 m-0">
                {shiftGroups(job, t).map((g) => <li key={g}>{g}</li>)}
              </ul>
            </div>
          )}
          {commute && originName && (
            <p className="m-0 mt-1 text-secondary">
              {commuteLine(commute, originName, t)}
            </p>
          )}
          <FactsLine job={job} needs={needs} />
          <div className="flex flex-wrap gap-2 mt-2">
            {shown.map((l) => (
              <Chip key={l.id} title={l.why}>{labelText(l.id, t)}</Chip>
            ))}
            {job.work_mode === 'remote' && <Chip>{t('common.remote')}</Chip>}
            {(job.commitments ?? []).map((c) => (
              <Chip key={c}>{t(`commit.${c}` as Key)}</Chip>
            ))}
            {job.event && <Chip tone="yes">{t('jobs.atevent')}</Chip>}
          </div>
        </div>
        <div className="text-end flex flex-col items-end gap-2 shrink-0 ms-auto">
          {job.stale
            ? <Chip tone="wait">{t('jobs.notconfirmed')}</Chip>
            : <span className="text-secondary">{daysAgoText(job.confirmed_days_ago, t)}</span>}
          <div className="flex gap-2 mt-auto">
            {saveBtn}
            {onShowOnMap && job.work_mode !== 'remote' && (
              <button type="button" className="btn btn-quiet relative z-[1]"
                      style={{ minHeight: 44, padding: '6px 14px' }}
                      aria-label={`${t('jobs.openonmap')}: ${job.title}`}
                      onClick={() => onShowOnMap(job.id)}>
                {t('jobs.openonmap')}
              </button>
            )}
          </div>
        </div>
      </div>
      {actions && <div className="relative z-[1]">{actions}</div>}
    </article>
  )
}
