import { Link } from 'react-router-dom'
import { MonitorPlay, DoorOpen, Coffee, Video } from 'lucide-react'
import { useI18n } from '../i18n/i18n'
import type { EventSummary, NeedEntry } from '../types'
import { useAuth } from '../lib/auth'

const mins = (hhmm: string) =>
  parseInt(hhmm.slice(0, 2), 10) * 60 + parseInt(hhmm.slice(3, 5), 10)
const hhmm = (m: number) =>
  `${String(Math.floor(m / 60)).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`

/** Online event-day lobby (spec §9.7): programme with a Live-now marker,
 * stage Jitsi room + who pitches when, virtual booths, lounge, privacy
 * note and a camera-test link. */
export default function OnlineLobby({ ev, now, employers }: {
  ev: EventSummary
  now: Date
  employers: NeedEntry[]
}) {
  const { t } = useI18n()
  const { user } = useAuth()
  const nowMin = now.getHours() * 60 + now.getMinutes()
  const stageUrl = `https://meet.jit.si/EspooTM-${ev.id}-stage`
  const testUrl =
    `https://meet.jit.si/EspooTM-test-${(user?.name || 'guest').split(' ')[0].toLowerCase()}`
  const pitchItem = ev.programme.find((p) => p.kind === 'pitch')
  const slots: { time: string; name: string; employer_id: string }[] = []
  if (pitchItem && employers.length) {
    const s = mins(pitchItem.start)
    const span = (mins(pitchItem.end ?? pitchItem.start) - s)
                 / employers.length
    employers.forEach((e, i) => slots.push({
      time: hhmm(Math.round(s + i * span)),
      name: e.employer_name ?? '', employer_id: e.employer_id,
    }))
  }
  return (
    <section className="card p-5 grid gap-4" aria-labelledby="lobby-h">
      <h2 id="lobby-h" className="m-0 flex items-center gap-2">
        <Video size={22} aria-hidden="true" /> {t('ev.lobby.title')}</h2>

      <a href={stageUrl} target="_blank" rel="noreferrer"
         className="btn btn-primary inline-flex items-center gap-2"
         style={{ minHeight: 52, fontSize: '1.1rem' }}>
        <MonitorPlay size={20} aria-hidden="true" />
        {t('ev.lobby.stage')}</a>

      <div>
        <h3 className="m-0" style={{ fontSize: '1rem' }}>
          {t('ev.programme')}</h3>
        <ul className="m-0 mt-1 p-0 list-none grid gap-1">
          {ev.programme.map((p, i) => {
            const live = nowMin >= mins(p.start) &&
                         nowMin < mins(p.end ?? p.start)
            return (
              <li key={i} className="flex gap-2 items-center flex-wrap">
                <span className="text-secondary"
                      style={{ minWidth: 90 }}>
                  {p.start}–{p.end}</span>
                <span>{p.title}</span>
                {live && (
                  <span className="chip yes" role="status">
                    {t('ev.lobby.livenow')}</span>)}
              </li>
            )
          })}
        </ul>
      </div>

      {slots.length > 0 && (
        <div>
          <h3 className="m-0" style={{ fontSize: '1rem' }}>
            {t('ev.lobby.pitches')}</h3>
          <ul className="m-0 mt-1 ps-5">
            {slots.map((s) => (
              <li key={s.employer_id}>
                <strong>{s.time}</strong> — {s.name}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="flex gap-2 flex-wrap">
        <span className="chip inline-flex items-center gap-1">
          <DoorOpen size={14} aria-hidden="true" />
          {t('ev.lobby.booths')}:</span>
        {employers.map((e) => (
          <Link key={e.employer_id} className="chip"
                to={`/events/${ev.id}/booths/${e.employer_id}`}>
            {e.employer_name}</Link>
        ))}
        <Link className="chip inline-flex items-center gap-1"
              to={`/events/${ev.id}/lounge`}>
          <Coffee size={14} aria-hidden="true" />
          {t('ev.lobby.lounge')}</Link>
      </div>

      <p className="m-0 text-secondary" style={{ fontSize: '.9rem' }}>
        {t('ev.lobby.jitsi')}{' '}
        <a href={testUrl} target="_blank" rel="noreferrer">
          {t('ev.lobby.testcam')}</a>
      </p>
    </section>
  )
}
