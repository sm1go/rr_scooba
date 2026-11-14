import { useEffect, useRef, useState } from 'react'
import { useParams } from 'react-router-dom'
import QRCode from 'qrcode'
import { api, ApiError } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import { ErrorBox } from '../components/ui'

type Pass = { token: string; event_id: string; name: string
             first_name: string; visitor_code: string | null }

/** Personal QR pass — show it on your phone at the event. */
export default function EventPass() {
  const { id } = useParams()
  const { t } = useI18n()
  const [p, setP] = useState<Pass | null>(null)
  const [err, setErr] = useState('')
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    api<Pass>(`/api/me/events/${id}/pass`).then(setP)
      .catch((e) => setErr(e instanceof ApiError ? e.message
                           : t('common.error')))
  }, [id, t])

  useEffect(() => {
    if (!p || !canvasRef.current) return
    const base = import.meta.env.VITE_PUBLIC_BASE_URL
      || window.location.origin
    QRCode.toCanvas(canvasRef.current, `${base}/p/${p.token}`,
                    { width: 280, margin: 2 })
  }, [p])

  if (err) return <ErrorBox>{err}</ErrorBox>
  if (!p) return <p>{t('common.loading')}</p>

  return (
    <div className="grid gap-4 justify-items-center text-center">
      <div>
        <h1 data-page-title tabIndex={-1} className="mb-1">
          {t('pass.title')}</h1>
        <p className="m-0 text-lg">{p.first_name} — {p.name}</p>
      </div>
      <canvas ref={canvasRef} className="card p-3"
              aria-label={t('pass.qr')} />
      {p.visitor_code && (
        <p className="m-0 text-2xl font-semibold">
          {t('event.number')}: {p.visitor_code}</p>
      )}
      <p className="m-0 text-secondary max-w-prose">{t('pass.consent')}</p>
      <p className="m-0 text-secondary max-w-prose">{t('pass.bright')}</p>
      <button type="button" className="btn btn-quiet"
              onClick={() => window.print()}>{t('pass.print')}</button>
      <p className="m-0 text-secondary max-w-prose">{t('pass.how')}</p>
    </div>
  )
}
