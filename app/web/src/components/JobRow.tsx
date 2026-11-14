import type { ReactNode } from 'react'
import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Bookmark } from 'lucide-react'
import type { Job } from '../types'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import { Chip } from './ui'
import { daysAgoText, jobLine } from '../lib/format'
import { commuteLine, getCommute } from '../lib/commute'
import { useConfig } from '../lib/config'

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

/** One job row — the whole card opens the job (title is the real link).
    Max 3 neutral label chips + "+N more"; confirmed state top-right. */
export default function JobRow({
  job, selected, onShowOnMap, districtName, saved, onToggleSave, actions,
  originDistrict, originName,
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
}) {
  const { t } = useI18n()
  const cfg = useConfig()
  const nav = useNavigate()
  const ref = useRef<HTMLElement>(null)
  const [commute, setCommute] = useState(job.commute ?? null)
  const [asked, setAsked] = useState(job.commute !== undefined)
  const url = `/jobs/${job.id}${originDistrict ? `?district=${originDistrict}` : ''}`
  const open = () => nav(url)
  const shown = job.labels.slice(0, 3)
  const rest = job.labels.length - shown.length

  // fetch the commute lazily when the row scrolls into view (§5);
  // max 4 requests at a time, cached per job+district
  useEffect(() => {
    if (!cfg.commute || !originDistrict || asked || job.lat == null
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
  }, [cfg.commute, originDistrict, asked, job])

  return (
    <article
      ref={ref}
      id={`job-row-${job.id}`}
      className="card p-5 mb-3 cursor-pointer"
      style={selected ? { outline: '3px solid var(--color-yes)' } : undefined}
      aria-current={selected || undefined}
      onClick={open}
      onKeyDown={(e) => { if (e.key === 'Enter') open() }}>
      <div className="flex flex-wrap justify-between gap-3">
        <div className="min-w-0 flex-1" style={{ minWidth: 'min(100%, 340px)' }}>
          <Link to={url} className="no-underline"
                style={{ color: 'var(--color-ink)' }}
                onClick={(e) => e.stopPropagation()}>
            <h3 className="m-0 font-display" style={{ fontSize: '1.25rem' }}>
              {job.title}
            </h3>
          </Link>
          <p className="m-0 mt-1 text-secondary">
            {job.employer?.name} · {districtName ?? job.district}
            {job.distance_km != null && ` · ${job.distance_km} km`}
          </p>
          <p className="m-0 mt-1">{jobLine(job, t)}</p>
          {commute && originName && (
            <p className="m-0 mt-1 text-secondary">
              {commuteLine(commute, originName, t)}
            </p>
          )}
          <div className="flex flex-wrap gap-2 mt-2">
            {shown.map((l) => (
              <Chip key={l.id} title={l.why}>{labelText(l.id, t)}</Chip>
            ))}
            {rest > 0 && (
              <Chip title={job.labels.slice(3).map((l) => labelText(l.id, t)).join(', ')}>
                +{rest} {t('jobs.andmore')}
              </Chip>
            )}
            {job.work_mode === 'remote' && <Chip>{t('common.remote')}</Chip>}
            {job.event && <Chip tone="yes">{t('jobs.atevent')}</Chip>}
          </div>
        </div>
        <div className="text-right flex flex-col items-end gap-2 shrink-0 ml-auto">
          {job.stale
            ? <Chip tone="wait">{t('jobs.notconfirmed')}</Chip>
            : <span className="text-secondary">{daysAgoText(job.confirmed_days_ago, t)}</span>}
          <div className="flex gap-2 mt-auto">
            {onToggleSave && (
              <button type="button" className="btn btn-quiet"
                      style={{ minHeight: 44, padding: '6px 12px' }}
                      aria-pressed={saved}
                      aria-label={saved ? t('common.saved') : t('common.save')}
                      onClick={(e) => { e.stopPropagation(); onToggleSave(job) }}>
                <Bookmark size={20} fill={saved ? 'currentColor' : 'none'} aria-hidden="true" />
              </button>
            )}
            {onShowOnMap && job.work_mode !== 'remote' && (
              <button type="button" className="btn btn-quiet"
                      style={{ minHeight: 44, padding: '6px 14px' }}
                      onClick={(e) => { e.stopPropagation(); onShowOnMap(job.id) }}>
                {t('jobs.openonmap')}
              </button>
            )}
          </div>
        </div>
      </div>
      {actions && <div onClick={(e) => e.stopPropagation()}>{actions}</div>}
    </article>
  )
}
