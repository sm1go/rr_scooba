import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, Coffee, UserPlus, UserCheck } from 'lucide-react'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { LoungeData } from '../types'

/** Networking lounge (spec §9.7): first names only, join/leave,
 * one-click connect between members. */
export default function LoungePage() {
  const { id } = useParams()
  const { t } = useI18n()
  const [data, setData] = useState<LoungeData | null>(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState('')

  const load = () => {
    if (!id) return
    api<LoungeData>(`/api/events/${id}/lounge`)
      .then(setData).catch((e) => setErr(e.message))
  }
  useEffect(load, [id])

  const toggle = async () => {
    setBusy('toggle')
    try {
      await api(`/api/events/${id}/lounge`,
                { method: data?.joined ? 'DELETE' : 'PUT' })
      load()
    } catch (e) { setErr((e as Error).message) }
    finally { setBusy('') }
  }

  const connect = async (uid: string) => {
    setBusy(uid)
    try {
      await api(`/api/events/${id}/lounge/connect/${uid}`,
                { method: 'POST' })
      load()
    } catch (e) { setErr((e as Error).message) }
    finally { setBusy('') }
  }

  if (err) return <p className="card p-5" role="alert">{err}</p>
  if (!data) return <p>{t('common.loading')}</p>

  return (
    <div className="grid gap-4">
      <p className="m-0">
        <Link to={`/events/${id}`} className="inline-flex items-center gap-1">
          <ArrowLeft size={16} aria-hidden="true" /> {t('booth.back')}
        </Link>
      </p>
      <header className="card p-5 flex gap-3 items-center flex-wrap">
        <Coffee size={28} aria-hidden="true" />
        <div className="flex-1" style={{ minWidth: 0 }}>
          <h1 className="m-0" style={{ fontSize: '1.4rem' }}>
            {t('lounge.title')}</h1>
          <p className="m-0 mt-1 text-secondary">{t('lounge.note')}</p>
        </div>
        <button type="button"
                className={`btn ${data.joined ? 'btn-secondary'
                                               : 'btn-primary'}`}
                disabled={busy === 'toggle'} onClick={toggle}>
          {data.joined ? t('lounge.leave') : t('lounge.join')}</button>
      </header>

      {!data.joined && (
        <p className="card p-5 text-secondary m-0">{t('lounge.joinfirst')}</p>
      )}
      {data.joined && (
        <section aria-labelledby="lm-h">
          <h2 id="lm-h" style={{ fontSize: '1.1rem' }}>
            {t('lounge.members')} ({data.members.length})</h2>
          <ul className="grid gap-3 p-0 m-0 list-none"
              style={{ gridTemplateColumns:
                       'repeat(auto-fill, minmax(260px, 1fr))' }}>
            {data.members.map((m) => (
              <li key={m.user_id} className="card p-4 grid gap-1">
                <strong>{m.first_name}</strong>
                {m.looking_for && (
                  <span className="text-secondary">
                    {t('lounge.looking')}: {m.looking_for}</span>)}
                {m.done && (
                  <span className="text-secondary">
                    {t('lounge.done')}: {m.done}</span>)}
                <span>
                  {m.connected ? (
                    <span className="chip yes inline-flex items-center gap-1">
                      <UserCheck size={14} aria-hidden="true" />
                      {t('lounge.connected')}</span>
                  ) : (
                    <button type="button" className="btn btn-secondary"
                            style={{ minHeight: 44 }}
                            disabled={busy === m.user_id}
                            onClick={() => connect(m.user_id)}>
                      <UserPlus size={16} aria-hidden="true" />
                      {' '}{t('lounge.connect')}</button>
                  )}
                </span>
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}
