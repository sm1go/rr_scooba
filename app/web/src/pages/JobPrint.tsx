import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import QRCode from 'qrcode'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Job } from '../types'
import { daysAgoText, hoursLine, payLine, shiftGroups, shiftNote } from '../lib/format'

/** /jobs/:id/print — a paper notice with a QR code back to the job. */
export default function JobPrint() {
  const { id } = useParams()
  const { t } = useI18n()
  const [job, setJob] = useState<Job | null>(null)
  const [err, setErr] = useState(false)
  const qrRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    api<Job>(`/api/jobs/${id}`).then(setJob).catch(() => setErr(true))
  }, [id])

  useEffect(() => {
    if (!job || !qrRef.current) return
    const base = (import.meta.env.VITE_PUBLIC_BASE_URL as string | undefined)
      || window.location.origin
    QRCode.toCanvas(qrRef.current, `${base}/jobs/${job.id}`, { width: 180 })
      .catch(() => undefined)
  }, [job])

  if (err) return <p>{t('err.gone')}</p>
  if (!job) return <p>{t('common.loading')}</p>
  const known = job.conditions.filter((c) => c.value !== 'unknown')
  const base = (import.meta.env.VITE_PUBLIC_BASE_URL as string | undefined)
    || window.location.origin
  const shortUrl = `${base.replace(/^https?:\/\//, '')}/jobs/${job.id}`

  return (
    <div className="print-sheet max-w-3xl mx-auto">
      <div className="no-print flex justify-between items-center mb-4">
        <Link to={`/jobs/${job.id}`} className="text-secondary">{`← ${t('common.back')}`}</Link>
        <button type="button" className="btn btn-primary" onClick={() => window.print()}>
          {t('print.print')}
        </button>
      </div>

      <h1 data-page-title tabIndex={-1} className="m-0 font-display" style={{ fontSize: '2.4rem', lineHeight: 1.15 }}>
        {job.title}
      </h1>
      <p className="m-0 mt-2" style={{ fontSize: '1.25rem' }}>
        {job.employer?.name} · {job.address}
      </p>

      <dl className="print-facts">
        <div><dt>{t('job.pay')}</dt><dd>{payLine(job, t)}</dd></div>
        <div><dt>{t('job.when')}</dt><dd>
          {job.rota && <span className="block">{t('job.rota')}</span>}
          {shiftGroups(job, t).map((g) => <span key={g} className="block">{g}</span>)}
          {shiftNote(job, t) && !job.rota && <span className="block">{shiftNote(job, t)}</span>}
          {hoursLine(job, t) && <span className="block">{hoursLine(job, t)}</span>}
        </dd></div>
        {job.contract && (
          <div><dt>{t('job.contract')}</dt><dd>{t(`contract.${job.contract}` as Key)}</dd></div>
        )}
      </dl>

      <h2 className="print-h2">{t('job.whatyoudo')}</h2>
      <ul className="m-0 ps-5" style={{ fontSize: '1.1rem' }}>
        {job.duties.map((d, i) => <li key={i}>{d}</li>)}
      </ul>

      {(known.length > 0 || job.lifting) && (
        <>
          <h2 className="print-h2">{t('job.conditions')}</h2>
          <ul className="list-none m-0 p-0" style={{ fontSize: '1.1rem' }}>
            {known.map((c) => (
              <li key={c.key}>
                <strong>{c.value === 'yes' ? '✓' : '✗'}</strong>{' '}
                {t(`cond.${c.key}` as Key)}: {c.value === 'yes' ? t('common.yes') : t('common.no')}
              </li>
            ))}
            {job.lifting && <li>{t('job.lifting')}: {job.lifting}</li>}
          </ul>
        </>
      )}

      <div className="print-qr">
        <canvas ref={qrRef} aria-label={t('print.scantext')} />
        <div>
          <p className="m-0 font-medium" style={{ fontSize: '1.2rem' }}>{t('print.scantext')}</p>
          <p className="m-0 mt-1">{t('print.nophone')}</p>
          <p className="m-0 mt-2 text-secondary">
            {t('print.lastconfirmed')}: {job.stale
              ? t('jobs.notconfirmed')
              : daysAgoText(job.confirmed_days_ago, t)}
          </p>
        </div>
      </div>

      <div className="tear-off" aria-hidden="true">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="tear-tab">
            <strong>{job.title.length > 34 ? `${job.title.slice(0, 33)}…` : job.title}</strong>
            <span>{shortUrl}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
