import { useEffect, useRef, useState } from 'react'
import QRCode from 'qrcode'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'

type Pass = { token: string; event_id: string; name: string
             first_name: string; visitor_code: string | null }

/** Personal QR pass, inline variant for the Meet step (§8.1). */
export default function PassInline({ eventId }: { eventId: string }) {
  const { t } = useI18n()
  const [p, setP] = useState<Pass | null>(null)
  const canvasRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    api<Pass>(`/api/me/events/${eventId}/pass`).then(setP).catch(() => {})
  }, [eventId])
  useEffect(() => {
    if (!p || !canvasRef.current) return
    const base = import.meta.env.VITE_PUBLIC_BASE_URL
      || window.location.origin
    QRCode.toCanvas(canvasRef.current, `${base}/p/${p.token}`,
                    { width: 220, margin: 2 })
  }, [p])
  if (!p) return null
  return (
    <div className="card p-4 grid gap-2 justify-items-center text-center">
      <canvas ref={canvasRef} aria-label={t('pass.qr')} />
      {p.visitor_code && (
        <p className="m-0 text-2xl font-semibold">
          {t('event.number')}: {p.visitor_code}</p>
      )}
      <p className="m-0 text-secondary max-w-prose">{t('pass.consent')}</p>
    </div>
  )
}
