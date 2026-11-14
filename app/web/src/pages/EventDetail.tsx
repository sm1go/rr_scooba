import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type {
  Connection,
  EventAfterData,
  EventRecord,
  EventDetailData, EventSummary, MyEventData,
  NeedEntry, TalentCardData,
} from '../types'
import { DAYS, PARTS } from '../types'
import { ErrorBox, ErrorState, Section, Toggle } from '../components/ui'
import { Tabs } from '../components/Tabs'
import ScanBox from '../components/ScanBox'
import CompanyLogo from '../components/CompanyLogo'
import BoothPlan from '../components/BoothPlan'
import { useConfig } from '../lib/config'
import EventPage from './EventPage'

const CARD_LANGS = ['en', 'fi', 'sv', 'ru', 'ar', 'et', 'fa', 'sq', 'uk']

function fmtDate(iso: string) {
  try {
    return new Date(iso + 'T00:00:00').toLocaleDateString(
      document.documentElement.lang || 'en',
      { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  } catch { return iso }
}
function fmtTime(iso: string) {
  return iso.includes('T') ? iso.split('T')[1].slice(0, 5) : iso
}
const toggleIn = (arr: string[], v: string) =>
  arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]

/** One translated fit-reason chip. */
function Fit({ f }: { f: { key: string; [k: string]: unknown } }) {
  const { t } = useI18n()
  const text = t(`ev.fit.${f.key}` as Key, f as Record<string, string>)
  return (
    <span className="chip" style={{ background: 'var(--color-yes-bg)' }}>
      {text}
    </span>
  )
}

function NeedCardView({ e, registered, onToggleInterest, interestCount, limit }: {
  e: NeedEntry
  registered: boolean
  interestCount: number
  limit: number
  onToggleInterest: (e: NeedEntry) => void
}) {
  const { t } = useI18n()
  const card = e.need!.card
  const [meets, setMeets] = useState<number[]>(e.meets ?? [])
  const [open, setOpen] = useState(false)

  return (
    <article className="card p-4 grid gap-2">
      <h3 className="m-0">
        <Link to={`/companies/${e.employer_id}`}>{e.employer_name}</Link>
      </h3>
      {e.company_badges?.includes('employer_answered') && (
        <span className="chip" style={{ background: 'var(--color-yes-bg)' }}>
          {t('badge.employer_answered')}</span>
      )}
      {e.need!.need_by === 'advisor' && (
        <p className="text-secondary m-0">{t('ev.byadvisor')}</p>
      )}
      {card.first_week.length > 0 && (
        <div>
          <strong>{t('ev.firstweek')}</strong>
          <ul className="m-0 ps-5">{card.first_week.map((x, i) => <li key={i}>{x}</li>)}</ul>
        </div>
      )}
      {card.must_haves.length > 0 && (
        <div>
          <strong>{t('ev.must')}</strong>
          <ul className="m-0 ps-5">
            {card.must_haves.map((m, i) => (
              <li key={i}>{m.text}
                {m.why && <span className="text-secondary"> — {m.why}</span>}
                {registered && e.interested !== undefined && (
                  <label className="ms-2 inline-flex items-center gap-1">
                    <input type="checkbox" checked={meets.includes(i)}
                           onChange={() =>
                             setMeets(meets.includes(i)
                               ? meets.filter((x) => x !== i) : [...meets, i])} />
                    <span>{t('ev.thisisme')}</span>
                  </label>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      {card.languages.length > 0 && (
        <p className="m-0"><strong>{t('ev.langs')}</strong>{' '}
          {card.languages.map((l) => `${l.name} ${l.level}${l.task ? ` (${l.task})` : ''}`).join(', ')}
        </p>
      )}
      {card.will_teach.length > 0 && (
        <p className="m-0"><strong>{t('ev.teach')}</strong>{' '}{card.will_teach.join(' · ')}</p>
      )}
      {e.fit && e.fit.length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {e.fit.map((f, i) => <Fit key={i} f={f} />)}
        </div>
      )}
      {registered && (
        <div className="flex gap-2 items-center flex-wrap">
          {!e.interested && interestCount >= limit ? (
            <span className="text-secondary">{t('ev.limit', { n: limit })}</span>
          ) : !e.interested && !open ? (
            <button type="button" className="btn btn-secondary"
                    onClick={() => setOpen(true)}>{t('ev.interested')}</button>
          ) : e.interested ? (
            <>
              <span className="font-medium" style={{ color: 'var(--color-brand)' }}>
                {t('ev.interested_on')}
              </span>
              <button type="button" className="btn btn-secondary"
                      onClick={() => onToggleInterest(e)}>{t('ev.notinterested')}</button>
            </>
          ) : (
            <button type="button" className="btn btn-primary"
                    onClick={() => onToggleInterest({ ...e, meets })}>
              {t('ev.interested.send')}
            </button>
          )}
        </div>
      )}
    </article>
  )
}

function RegisterForm({ ev, onDone }: {
  ev: EventSummary; onDone: (r: MyEventData['registration']) => void
}) {
  const { t } = useI18n()
  const [timeGroup, setTimeGroup] = useState(ev.time_groups[0]?.id ?? 'A')
  const [cardLang, setCardLang] = useState('en')
  const [lookingFor, setLookingFor] = useState('')
  const [done, setDone] = useState(['', '', ''])
  const [district, setDistrict] = useState('')
  const [availability, setAvailability] = useState<string[]>([])
  const [districts, setDistricts] = useState<{ id: string; name: string }[]>([])
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [aiBusy, setAiBusy] = useState(false)
  const cfg = useConfig()

  useEffect(() => {
    api<{ districts: { id: string; name: string }[] }>('/api/catalog')
      .then((c) => setDistricts(c.districts)).catch(() => {})
  }, [])

  const submit = async (e: FormEvent) => {
    e.preventDefault()
    setErr(''); setBusy(true)
    try {
      const card: TalentCardData = {
        looking_for: lookingFor.trim(),
        done: done.filter((d) => d.trim()).map((d) => ({ text: d.trim(), own_words: d.trim() })),
        district, availability,
      }
      const d = await api<{ registration: MyEventData['registration'] }>(
        `/api/events/${ev.id}/register`,
        { body: { time_group: timeGroup, card_language: cardLang, card } })
      onDone(d.registration)
    } catch (e2) {
      setErr(e2 instanceof ApiError ? e2.message : t('common.error'))
    } finally { setBusy(false) }
  }

  return (
    <form onSubmit={submit} className="card p-4 grid gap-4">
      <h3 className="m-0">{t('ev.register')}</h3>
      <fieldset className="border-0 p-0 m-0">
        <legend className="font-medium mb-1">{t('ev.timegroup')}</legend>
        <div className="flex gap-2 flex-wrap">
          {ev.time_groups.map((g) => (
            <Toggle key={g.id} pressed={timeGroup === g.id}
                    onClick={() => setTimeGroup(g.id)}>
              {t('ev.from', { t: g.entry })}
            </Toggle>
          ))}
        </div>
      </fieldset>
      <label className="grid gap-1">
        <span className="font-medium">{t('ev.cardlang')}</span>
        <select value={cardLang} onChange={(e) => setCardLang(e.target.value)}
                className="input" style={{ maxWidth: 260 }}>
          {CARD_LANGS.map((l) => <option key={l} value={l}>{l}</option>)}
        </select>
      </label>
      <label className="grid gap-1">
        <span className="font-medium">{t('ev.q1')}</span>
        <input className="input" value={lookingFor} required maxLength={140}
               onChange={(e) => setLookingFor(e.target.value)} />
      </label>
      {[0, 1, 2].map((i) => (
        <label key={i} className="grid gap-1">
          <span className="font-medium">{t(`ev.done${i + 1}` as Key)}</span>
          <input className="input" value={done[i]} required={i === 0} maxLength={140}
                 onChange={(e) => setDone(done.map((d, j) => j === i ? e.target.value : d))} />
        </label>
      ))}
      {cfg.ai && (
        <button type="button" className="link text-left"
                onClick={async () => {
                  setAiBusy(true); setErr('')
                  try {
                    const r = await api<{ lines: string[] }>(
                      '/api/ai/event-card',
                      { body: { items: done.filter((d) => d.trim()).slice(0, 3) } })
                    setDone(done.map((d, i) => r.lines[i] ?? d))
                  } catch (e2) {
                    setErr(e2 instanceof ApiError ? e2.message : t('common.error'))
                  } finally { setAiBusy(false) }
                }}
                disabled={aiBusy || !done.some((d) => d.trim())}>
          {t('ev.ai.help')}
        </button>
      )}
      <label className="grid gap-1">
        <span className="font-medium">{t('ev.district')}</span>
        <select className="input" style={{ maxWidth: 260 }} value={district}
                onChange={(e) => setDistrict(e.target.value)}>
          <option value="">{t('common.anywhere')}</option>
          {districts.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
        </select>
      </label>
      <fieldset className="border-0 p-0 m-0">
        <legend className="font-medium mb-1">{t('ev.avail')}</legend>
        <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
          <div />
          {PARTS.map((x) => <strong key={x}>{t(`part.${x}` as Key)}</strong>)}
          {DAYS.map((d) => (
            <div key={d} className="contents">
              <strong className="self-center">{t(`dayfull.${d}` as Key)}</strong>
              {PARTS.map((x) => {
                const s = `${d}-${x}`
                return (
                  <Toggle key={s} pressed={availability.includes(s)}
                          onClick={() => setAvailability(toggleIn(availability, s))}
                          className="justify-center">
                    {t(`part.${x}` as Key)}
                  </Toggle>
                )
              })}
            </div>
          ))}
        </div>
      </fieldset>
      {err && <ErrorBox>{err}</ErrorBox>}
      <div><button className="btn btn-primary" disabled={busy}>{t('ev.register.send')}</button></div>
    </form>
  )
}

export default function EventDetail() {
  const { id } = useParams()
  const { t } = useI18n()
  const { user } = useAuth()
  const [ev, setEv] = useState<EventDetailData | null>(null)
  const [needs, setNeeds] = useState<NeedEntry[] | null>(null)
  const [my, setMy] = useState<MyEventData | null>(null)
  const [conns, setConns] = useState<Connection[]>([])
  const [records, setRecords] = useState<EventRecord[]>([])
  const [afterData, setAfterData] = useState<EventAfterData | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const [showForm, setShowForm] = useState(false)

  const isResident = user?.role === 'resident'

  const load = () => {
    setErr(null)
    api<EventDetailData>(`/api/events/${id}`).then(setEv).catch(setErr)
    api<EventAfterData>(`/api/events/${id}/after`)
      .then(setAfterData).catch(() => setAfterData(null))
    if (isResident) {
      api<MyEventData>(`/api/events/${id}/my`).then(setMy).catch(() => setMy(null))
    api<{ connections: Connection[] }>('/api/me/connections')
      .then((d) => setConns(d.connections)).catch(() => {})
    api<{ records: EventRecord[] }>('/api/me/event-records')
      .then((r) => setRecords(r.records)).catch(() => setRecords([]))
    }
  }
  useEffect(load, [id, user?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  // need cards: the server decides who may see them (403 before publish)
  useEffect(() => {
    if (!ev) return
    api<{ cards: NeedEntry[] }>(`/api/events/${id}/needs`)
      .then((d) => setNeeds(d.cards)).catch(() => setNeeds(null))
  }, [ev?.id, id, my?.registration?.id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (err) return <ErrorState err={err} goneLabel={t('ev.gone')} retryLabel={t('err.retry')} onRetry={load} backTo="/" backLabel={t('nav.home')} />
  if (!ev) return <p>{t('common.loading')}</p>

  const reg = my?.registration ?? null
  const interestCount = my?.interests.length ?? 0
  const limit = my?.interest_limit ?? 5

  const toggleInterest = async (e: NeedEntry) => {
    try {
      if (e.interested) {
        await api(`/api/events/${id}/interests/${e.employer_id}`, { method: 'DELETE' })
      } else {
        await api(`/api/events/${id}/interests/${e.employer_id}`,
          { body: { meets: e.meets ?? [], language_levels: {} } })
      }
      const m = await api<MyEventData>(`/api/events/${id}/my`); setMy(m)
      const d = await api<{ cards: NeedEntry[] }>(`/api/events/${id}/needs`)
      setNeeds(d.cards)
    } catch (e2) { alert(e2 instanceof ApiError ? e2.message : t('common.error')) }
  }

  const before = (
    <div className="grid gap-6">
      {ev.description && <p className="max-w-prose">{ev.description}</p>}

      {ev.programme.length > 0 && (
        <Section title={t('ev.programme')}>
          <ul className="m-0 ps-5">
            {ev.programme.map((p, i) => (
              <li key={i}>
                {fmtTime(p.start)}{p.end ? `–${fmtTime(p.end)}` : ''} — {p.title || t(`ev.prog.${p.kind}` as Key)}
              </li>
            ))}
          </ul>
        </Section>
      )}

      <Section title={t('ev.employers.title', { n: ev.employers.length })}>
        <ul className="m-0 p-0 list-none grid gap-3 emp-tiles">
          {ev.employers.map((e) => {
            const firstLine = e.need?.card.first_week?.[0]
            return (
              <li key={e.employer_id} className="card p-4"
                  style={{ position: 'relative' }}>
                <Link to={`/companies/${e.employer_id}`}
                      className="flex gap-3 items-start stretched-link">
                  <CompanyLogo
                    employer={{ name: e.employer_name ?? '',
                                logo_color: e.logo_color, field: e.field }}
                    size={44} />
                  <span className="flex-1" style={{ minWidth: 0 }}>
                    <span className="block font-medium">{e.employer_name}</span>
                    {e.tagline &&
                      <span className="block text-secondary">{e.tagline}</span>}
                    <span className="block text-secondary">
                      {[
                        e.field ? t(`field.${e.field}` as Key) : '',
                        e.booth ? `${t('ev.booth')} ${e.booth}` : '',
                        e.open_jobs != null
                          ? t('ev.openjobs.n', { n: e.open_jobs }) : '',
                      ].filter(Boolean).join(' · ')}
                    </span>
                    {firstLine && (
                      <span className="block mt-1">
                        <strong>{t('ev.firstweek')}</strong> {firstLine}
                      </span>
                    )}
                  </span>
                </Link>
              </li>
            )
          })}
        </ul>
      </Section>

      <Section title={t('ev.needs')}>
        {!needs ? (
          <p>{t('ev.needs.soon', { d: fmtDate(ev.publish_date) })}</p>
        ) : (
          <div className="grid gap-3">
            {needs.map((e) => (
              <NeedCardView key={e.employer_id} e={e} registered={!!reg}
                            interestCount={interestCount} limit={limit}
                            onToggleInterest={toggleInterest} />
            ))}
            {needs.length === 0 && <p>{t('ev.needs.none')}</p>}
          </div>
        )}
      </Section>

      {reg && (
        <Section title={t('ev.meetings')}>
          {my!.meetings.length === 0 ? <p>{t('ev.meetings.none')}</p> : (
            <ul className="m-0 ps-5">
              {my!.meetings.map((m) => (
                <li key={m.id}>{fmtTime(m.starts_at)} — {m.employer_name}
                  {m.booth ? ` (${t('ev.booth')} ${m.booth})` : ''}</li>
              ))}
            </ul>
          )}
        </Section>
      )}

      {!user && (
        <div className="card p-4">
          <p className="mt-0">{t('ev.signin.cta')}</p>
          <div className="flex gap-2 flex-wrap">
            <Link to={`/sign-in?back=${encodeURIComponent(`/events/${id}`)}`}
                  className="btn btn-primary">{t('nav.signin')}</Link>
            <Link to="/help" className="btn btn-secondary">{t('ev.advisor.help')}</Link>
          </div>
        </div>
      )}
      {user && !isResident && <p className="text-secondary">{t('ev.resident.only')}</p>}
      {isResident && !reg && !showForm && (
        <button type="button" className="btn btn-primary" onClick={() => setShowForm(true)}>
          {t('ev.register')}
        </button>
      )}
      {isResident && !reg && showForm && (
        <RegisterForm ev={ev} onDone={() => { setShowForm(false); load() }} />
      )}
      {isResident && reg && (
        <div className="card p-4 flex gap-3 items-center flex-wrap">
          <strong>{reg.status === 'waitlist' ? t('ev.waitlist') : t('ev.registered')}</strong>
          <span className="text-secondary">
            {t('ev.timegroup')}: {ev.time_groups.find((g) => g.id === reg.time_group)?.entry ?? reg.time_group}
          </span>
          <button type="button" className="btn btn-secondary"
                  onClick={async () => {
                    await api(`/api/events/${id}/register`, { method: 'DELETE' })
                    load()
                  }}>{t('ev.cancel')}</button>
        </div>
      )}
    </div>
  )

  const queueJoin = async (employerId: string) => {
    try {
      await api(`/api/events/${id}/queue/${employerId}`, { method: 'PUT' })
      api<MyEventData>(`/api/events/${id}/my`).then(setMy).catch(() => {})
    } catch (e) { alert(e instanceof ApiError ? e.message : t('common.error')) }
  }
  const queueLeave = async (employerId: string) => {
    await api(`/api/events/${id}/queue/${employerId}`, { method: 'DELETE' })
    api<MyEventData>(`/api/events/${id}/my`).then(setMy).catch(() => {})
  }
  const queued = new Set(my?.queue.map((q) => q.employer_id) ?? [])

  const day = (
    <div className="grid gap-4">
      {id === 'ev-2026-11' ? <EventPage /> : !my ? (
        <p className="text-secondary">{t('ev.signin.cta')}</p>
      ) : (
        <>
          {my.visitor_code && (
            <div className="card p-4">
              <strong className="text-2xl tracking-widest block">
                {t('event.number')}: {my.visitor_code}
              </strong>
              <p className="text-secondary m-0">{t('event.numberwhy')}</p>
              <p className="m-0">
                <Link to={`/events/${id}/pass`} className="btn btn-quiet">
                  {t('pass.show')}</Link>
              </p>
            </div>
          )}
          <ScanBox eventId={id!} />
          {my.entry && my.registration && (
            <p className="m-0 font-medium">
              {t('ev.day.entry', { t: my.entry, g: my.registration.time_group })}
            </p>
          )}
          {my.meetings.length > 0 && (
            <Section title={t('ev.meetings')}>
              <ul className="m-0 ps-5">
                {my.meetings.map((m) => (
                  <li key={m.id} className="mb-1">
                    <strong>{fmtTime(m.starts_at)}</strong> — {m.employer_name}
                    {m.booth ? ` (${t('ev.booth')} ${m.booth})` : ''}
                    {m.need_line && (
                      <span className="block text-secondary">{m.need_line}</span>
                    )}
                  </li>
                ))}
              </ul>
            </Section>
          )}
          <BoothPlan
            employers={ev.employers.map((e) => ({
              id: e.employer_id, name: e.employer_name ?? '',
              booth: e.booth, field: e.field, logo_color: e.logo_color }))}
            inPlan={new Set(my.interests.map((i) => i.employer_id))}
          />
          <Section title={t('ev.day.queue.title')}>
            <ul className="grid gap-2 p-0 list-none">
              {ev.employers.map((e) => (
                <li key={e.employer_id}
                    className="flex gap-2 items-center flex-wrap">
                  <span className="flex-1" style={{ minWidth: 140 }}>
                    {e.employer_name}{e.booth ? ` (${t('ev.booth')} ${e.booth})` : ''}
                  </span>
                  {queued.has(e.employer_id) ? (
                    <button type="button" className="btn btn-secondary"
                            onClick={() => queueLeave(e.employer_id)}>
                      {t('ev.day.queue.leave')}
                    </button>
                  ) : (
                    <button type="button" className="btn btn-secondary"
                            onClick={() => queueJoin(e.employer_id)}>
                      {t('ev.day.queue.join')}
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </Section>
        </>
      )}
    </div>
  )

  const after = (
    <div className="grid gap-4">
      {afterData?.mine && afterData.mine.length > 0 && (
        <Section title={t('ev.after.earlier')}>
          <div className="grid gap-3">
            {afterData.mine.map((h) => (
              <div key={h.event_id} className="card p-4">
                <strong>{h.name}</strong>
                <span className="text-secondary"> — {fmtDate(h.date)}</span>
                {h.talks.length > 0 && (
                  <ul className="m-0 mt-2 ps-5">
                    {h.talks.map((tk, i) => (
                      <li key={i}>
                        <strong>{tk.employer}</strong>{' — '}
                        {tk.outcome
                          ? t(`ev.outcome.${tk.outcome}` as Key)
                          : t('ev.outcome.waiting')}
                        {tk.note &&
                          <span className="text-secondary"> — {tk.note}</span>}
                      </li>
                    ))}
                  </ul>
                )}
                {h.records.length > 0 && (
                  <ul className="m-0 mt-1 ps-5">
                    {h.records.map((r, i) => (
                      <li key={i}>
                        {t('ev.after.seen')} — <strong>{r.employer}</strong>
                        {r.observed.length > 0 && (
                          <span className="text-secondary">
                            {' '}({r.observed.join(', ')})</span>
                        )}
                      </li>
                    ))}
                  </ul>
                )}
                {h.badges.length > 0 && (
                  <div className="flex gap-2 flex-wrap mt-2">
                    {h.badges.map((b) => (
                      <span key={b.id} className="chip"
                            style={{ background: 'var(--color-yes-bg)' }}>
                        {t(`badge.${b.label || b.kind}` as Key,
                           { event: h.name })}
                      </span>
                    ))}
                  </div>
                )}
                {h.people.length > 0 && (
                  <p className="m-0 mt-1 text-secondary">
                    {t('ev.after.met')}:{' '}
                    {h.people.map((p2) =>
                      p2.name + (p2.company ? ` (${p2.company})` : '')
                    ).join(', ')}
                  </p>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}
      {afterData?.summaries && afterData.summaries.length > 0 && (
        <Section title={t('ev.after.howwent')}>
          <ul className="grid gap-2 p-0 list-none">
            {afterData.summaries.map((sm) => (
              <li key={sm.event_id} className="card p-3">
                <strong>{sm.name}</strong>
                <span className="text-secondary"> — {fmtDate(sm.date)}</span>
                <span className="block">
                  {t('ev.after.sum', {
                    e: sm.employers, p: sm.participants, t: sm.talks,
                    n: sm.next_steps, h: sm.hired })}
                  {sm.answered_in_7d_pct != null &&
                    ` · ${t('ev.after.sum7d', { n: sm.answered_in_7d_pct })}`}
                </span>
              </li>
            ))}
          </ul>
        </Section>
      )}
      {my && my.talks.length > 0 ? (
        <Section title={t('ev.talks')}>
          <ul className="grid gap-2 p-0 list-none">
            {my.talks.map((tk) => (
              <li key={tk.id} className="card p-3">
                <strong>{tk.employer_name}</strong>
                <span className="block">
                  {tk.outcome ? t(`ev.outcome.${tk.outcome}` as Key) : t('ev.outcome.waiting')}
                </span>
                {tk.note && <span className="block text-secondary">{tk.note}</span>}
              </li>
            ))}
          </ul>
        </Section>
      ) : <p className="text-secondary">{t('ev.talks.none')}</p>}
      {conns.filter((c) => c.event_id === id).length > 0 && (
        <Section title={t('ev.after.met')}>
          <ul className="grid gap-2 p-0 list-none">
            {conns.filter((c) => c.event_id === id).map((c) => (
              <li key={c.user_id} className="card p-3">
                <strong>{c.name}</strong>
                {c.company &&
                  <span className="text-secondary"> — {c.company}</span>}
                {(c.email || c.phone || c.public_link) && (
                  <span className="block">
                    {[c.email, c.phone, c.public_link]
                      .filter(Boolean).join(' · ')}</span>
                )}
              </li>
            ))}
          </ul>
        </Section>
      )}
      {records.length > 0 && (
        <Section title={t('ev.after.seen')}>
          <ul className="grid gap-2 p-0 list-none">
            {records.map((r, i) => (
              <li key={i} className="card p-3">
                <strong>{r.employer}</strong>
                <span className="block text-secondary">{fmtDate(r.date)}</span>
                <ul className="m-0 ps-5">
                  {r.observed.map((o, j) => <li key={j}>{o}</li>)}
                </ul>
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  )

  return (
    <div className="grid gap-4">
      <Link to="/" className="text-secondary">{`← ${t('common.back')}`}</Link>
      <div>
        <h1 data-page-title tabIndex={-1} className="mb-1">{ev.name}</h1>
        <p className="m-0">
          {fmtDate(ev.date)} · {fmtTime(ev.starts_at)}–{fmtTime(ev.ends_at)} · {ev.venue}
          {ev.address ? `, ${ev.address}` : ''}
        </p>
        <p className="m-0 text-secondary">
          {t(`ev.phase.${ev.phase}` as Key)}
          {ev.registered > 0 ? ` · ${ev.registered} ${t('ev.going')}` : ''}
        </p>
      </div>
      <Tabs label={ev.name}
            initial={ev.phase === 'today' ? 1 : ev.phase === 'finished' ? 2 : 0}
            labels={[t('ev.tab.before'), t('ev.tab.day'), t('ev.tab.after')]}>
        {[before, day, after]}
      </Tabs>
    </div>
  )
}
