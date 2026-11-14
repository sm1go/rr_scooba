import { useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useI18n } from '../i18n/i18n'

/** Camera scan (BarcodeDetector + getUserMedia) with a typed fallback.
 *  Employer mode also accepts the 4-digit visitor number. */
export default function ScanBox({ eventId, allowVisitorCode }: {
  eventId: string
  allowVisitorCode?: boolean
}) {
  const { t } = useI18n()
  const nav = useNavigate()
  const [open, setOpen] = useState(false)
  const [value, setValue] = useState('')
  const [err, setErr] = useState('')
  const [camFail, setCamFail] = useState(false)
  const videoRef = useRef<HTMLVideoElement | null>(null)
  const streamRef = useRef<MediaStream | null>(null)

  const stop = () => {
    streamRef.current?.getTracks().forEach((tr) => tr.stop())
    streamRef.current = null
  }

  const goToken = async (text: string) => {
    setErr('')
    const m = /\/p\/([A-Za-z0-9_-]{22})/.exec(text)
    const token = m ? m[1]
      : /^[A-Za-z0-9_-]{22}$/.test(text.trim()) ? text.trim() : null
    if (token) { stop(); nav(`/p/${token}`); return }
    if (allowVisitorCode && /^\d{3,5}$/.test(text.trim())) {
      try {
        const d = await api<{ token: string }>(
          `/api/events/${eventId}/pass-by-code/${text.trim()}`)
        stop(); nav(`/p/${d.token}`); return
      } catch (e) {
        setErr(e instanceof ApiError ? e.message : t('p.nocode'))
        return
      }
    }
    setErr(t('p.nocode'))
  }

  const start = async () => {
    setOpen(true); setErr('')
    const BD = (window as { BarcodeDetector?: new (o?: object) => {
      detect: (v: CanvasImageSource) => Promise<{ rawValue: string }[]>
    } }).BarcodeDetector
    if (!BD || !navigator.mediaDevices?.getUserMedia) {
      setCamFail(true); return
    }
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' } })
      streamRef.current = stream
      const video = videoRef.current
      if (!video) { stop(); setCamFail(true); return }
      video.srcObject = stream
      await video.play()
      const det = new BD({ formats: ['qr_code'] })
      const tick = async () => {
        if (!streamRef.current) return
        try {
          const found = await det.detect(video)
          if (found.length) { await goToken(found[0].rawValue); return }
        } catch { /* keep trying */ }
        if (streamRef.current) setTimeout(tick, 600)
      }
      tick()
    } catch {
      stop(); setCamFail(true)
    }
  }

  return (
    <div>
      {!open ? (
        <button type="button" className="btn btn-quiet"
                onClick={start}>{t('p.scan')}</button>
      ) : (
        <div className="card p-3 grid gap-2" style={{ maxWidth: 360 }}>
          {!camFail && (
            <video ref={videoRef} muted playsInline
                   aria-label={t('p.scan')} style={{ width: '100%' }} />
          )}
          <label className="grid gap-1">
            <span>{t('p.fallback')}</span>
            <input className="input" value={value}
                   onChange={(e) => setValue(e.target.value)}
                   inputMode="text" />
          </label>
          {err && <p className="text-danger m-0">{err}</p>}
          <div className="flex gap-2">
            <button type="button" className="btn btn-primary"
                    onClick={() => goToken(value)}>{t('p.open')}</button>
            <button type="button" className="btn btn-quiet"
                    onClick={() => { stop(); setOpen(false) }}>
              {t('common.close')}</button>
          </div>
        </div>
      )}
    </div>
  )
}
