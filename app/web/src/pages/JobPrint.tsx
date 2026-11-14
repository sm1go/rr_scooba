import { useEffect, useRef, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import QRCode from 'qrcode'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Job } from '../types'
import { daysAgoText, hoursLine, payLine, shiftsLine } from '../lib/format'

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

  return (
    <div className="print-sheet max-w-3xl mx-auto">
      <div className="no-print flex justify-between items-center mb-4">
        <Link to={`/jobs/${job.id}`} className="text-secondary">{`← ${t('common.back')}`}</Link>
        <button type="button" className="btn btn-primary" onClick={() => window.print()}>
          {t('print.print')}
        </button>
      </div>

      <h1 data-page-title tabIndex={-1}>{job.title}</h1>
      <p style={{ fontSize: '1.2rem' }}>{job.employer?.name} — {job.address}</p>

      <h2>{t('job.whatyoudo')}</h2>
      <ul className="pl-5">
        {job.duties.map((d, i) => <li key={i}>{d}</li>)}
      </ul>

      <h2>{t('job.pay')}</h2>
      <p style={{ fontSize: '1.2rem', fontWeight: 600 }}>{payLine(job, t)}</p>

      <h2>{t('job.when')}</h2>
      <p>{shiftsLine(job, t)}</p>
      <p>{hoursLine(job, t)}</p>
      {job.contract && <p>{t(`contract.${job.contract}` as Key)}</p>}

      <h2>{t('job.conditions')}</h2>
      <ul className="pl-5">
        {job.conditions.filter((c) => c.value === 'yes').map((c) => (
          <li key={c.key}>{t(`cond.${c.key}` as Key)}</li>
        ))}
      </ul>

      <div className="flex gap-6 items-center mt-6">
        <canvas ref={qrRef} aria-label={t('print.scantext')} />
        <div>
          <p className="font-medium">{t('print.scantext')}</p>
          <p className="text-secondary">{t('print.nophone')}</p>
        </div>
      </div>

      <p className="text-secondary mt-6 border-t pt-3"
         style={{ borderColor: 'var(--color-hairline)' }}>
        {t('print.lastconfirmed')}: {job.stale
          ? t('jobs.notconfirmed')
          : daysAgoText(job.confirmed_days_ago, t)}
      </p>

      <div className="tear-off" aria-hidden="true">
        {Array.from({ length: 8 }).map((_, i) => (
          <div key={i} className="tear-tab">
            {job.title.slice(0, 28)}<br />{job.id}
          </div>
        ))}
      </div>
    </div>
  )
}
