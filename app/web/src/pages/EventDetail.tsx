import { useEffect, useRef, useState } from 'react'
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
import ScanBox from '../components/ScanBox'
import CompanyLogo from '../components/CompanyLogo'
import BoothPlan from '../components/BoothPlan'
import VenueMap from '../components/VenueMap'
import NeedCardView from '../components/NeedCardView'
import Stepper from '../components/Stepper'
import CardChooser from '../components/CardChooser'
import type { Meeting } from '../components/CardChooser'
import PassInline from '../components/PassInline'
import { useConfig } from '../lib/config'

const CARD_LANGS = ['en', 'fi', 'sv', 'ru', 'ar', 'et', 'fa', 'sq', 'uk']

function fmtDate(iso: string) {
  try {
    return new Date(iso.includes('T') ? iso : iso + 'T00:00:00')
      .toLocaleDateString(document.documentElement.lang || 'en',
        { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  } catch { return iso }
}
function fmtTime(iso: string) {
  return iso.includes('T') ? iso.split('T')[1].slice(0, 5) : iso
}
function fmtDateTime(iso: string) {
  return `${fmtDate(iso)} ${fmtTime(iso)}`
}
const toggleIn = (arr: string[], v: string) =>
  arr.includes(v) ? arr.filter((x) => x !== v) : [...arr, v]

/** Demo/real clock: fetch /api/demo/state once, tick every 30 s. */
function useNow() {
  const cfg = useConfig()
  const [offset, setOffset] = useState(0)
  const [, setTick] = useState(0)
  useEffect(() => {
    if (!cfg.demo) return
    api<{ now: string }>('/api/demo/state')
      .then((d) => setOffset(Date.parse(d.now) - Date.now()))
      .catch(() => {})
  }, [cfg.demo])
  useEffect(() => {
    const i = setInterval(() => setTick((x) => x + 1), 30000)
    return () => clearInterval(i)
  }, [])
  return new Date(Date.now() + offset)
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
  const now = useNow()
  const [ev, setEv] = useState<EventDetailData | null>(null)
  const [needs, setNeeds] = useState<NeedEntry[] | null>(null)
  const [my, setMy] = useState<MyEventData | null>(null)
  const [conns, setConns] = useState<Connection[]>([])
  const [records, setRecords] = useState<EventRecord[]>([])
  const [afterData, setAfterData] = useState<EventAfterData | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const [showForm, setShowForm] = useState(false)
  const [step, setStep] = useState(-1)
  const [respNote, setRespNote] = useState<Record<string, string>>({})
  const [respDlg, setRespDlg] = useState<string | null>(null)
  const meetsRef = useRef<Record<string, number[]>>({})

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
  const phase = ev.phase
  const choosingOpen = phase === 'registration'
  const matchingDone = phase !== 'registration'
  const meetings = (my?.meetings ?? []).slice()
    .sort((a, b) => a.starts_at.localeCompare(b.starts_at))
  const meetingOf = new Map(meetings.map((m) => [m.employer_id, m]))
  const online = ev.format === 'online'

  const refreshMy = async () => {
    const m = await api<MyEventData>(`/api/events/${id}/my`); setMy(m)
    const d = await api<{ cards: NeedEntry[] }>(`/api/events/${id}/needs`)
    setNeeds(d.cards)
  }

  const chooseInterest = async (e: NeedEntry) => {
    try {
      const r = await api<{ meeting?: Meeting | null }>(
        `/api/events/${id}/interests/${e.employer_id}`,
        { method: 'PUT',
          body: { meets: meetsRef.current[e.employer_id] ?? e.meets ?? [],
                  language_levels: {} } })
      await refreshMy()
      if (interestCount + 1 >= limit) setStep(2)   // auto-advance at 5
      return r
    } catch (e2) {
      alert(e2 instanceof ApiError ? e2.message : t('common.error'))
      return {}
    }
  }
  const takeBackInterest = async (e: NeedEntry) => {
    try {
      await api(`/api/events/${id}/interests/${e.employer_id}`,
                { method: 'DELETE' })
      await refreshMy()
    } catch (e2) {
      alert(e2 instanceof ApiError ? e2.message : t('common.error'))
    }
  }
  const takeBackByEmployer = async (employerId: string) => {
    try {
      await api(`/api/events/${id}/interests/${employerId}`,
                { method: 'DELETE' })
      await refreshMy()
    } catch (e2) {
      alert(e2 instanceof ApiError ? e2.message : t('common.error'))
    }
  }
  // list-view toggle on a card (same endpoints as the chooser)
  const toggleInterest = async (e: NeedEntry) => {
    if (e.interested) await takeBackInterest(e)
    else await chooseInterest(e)
  }

  const respond = async (talkId: string, response: string) => {
    try {
      await api(`/api/events/${id}/talks/${talkId}/response`, {
        body: { response, note: respNote[talkId] ?? '' } })
      setRespDlg(null)
      await refreshMy()
    } catch (e2) {
      alert(e2 instanceof ApiError ? e2.message : t('common.error'))
    }
  }

  const programmeSection = ev.programme.length > 0 && (
    <Section title={t('ev.programme')}>
      <ul className="m-0 ps-5">
        {ev.programme.map((p, i) => (
          <li key={i}>
            {fmtTime(p.start)}{p.end ? `–${fmtTime(p.end)}` : ''} — {p.title || t(`ev.prog.${p.kind}` as Key)}
          </li>
        ))}
      </ul>
    </Section>
  )

  const tilesSection = (
    <Section title={t('ev.employers.title', { n: ev.employers.length })}>
        <ul className="m-0 p-0 list-none grid emp-tiles">
          {ev.employers.map((e) => {
            const firstLine = e.need?.card.first_week?.[0]
            return (
              <li key={e.employer_id} className="card p-5 emp-tile">
                <Link to={`/companies/${e.employer_id}`}
                      className="emp-tile-link">
                  <div className="flex gap-3 items-start">
                    <CompanyLogo
                      employer={{ name: e.employer_name ?? '',
                                  logo_color: e.logo_color,
                                  field: e.field }}
                      size={48} />
                    <span className="flex-1 emp-tile-name">
                      {e.employer_name}</span>
                    {e.booth &&
                      <span className="chip emp-booth">{e.booth}</span>}
                  </div>
                  {e.tagline &&
                    <p className="m-0 mt-2 text-secondary clamp-2">
                      {e.tagline}</p>}
                  <div className="flex gap-2 flex-wrap mt-2">
                    {e.field &&
                      <span className="chip">
                        {t(`field.${e.field}` as Key)}</span>}
                    {e.open_jobs != null && (
                      <span className="chip">
                        {t('ev.openjobs.n', { n: e.open_jobs })}</span>)}
                  </div>
                  {firstLine && (
                    <div className="mt-auto emp-tile-weeks">
                      <span className="emp-tile-label">
                        {t('ev.firstweek.label')}</span>
                      <span className="block clamp-2">{firstLine}</span>
                    </div>
                  )}
                  {!firstLine && <span className="mt-auto" />}
                  <span className="emp-tile-cta">{t('co.see')}</span>
                </Link>
              </li>
            )
          })}
        </ul>
    </Section>
  )

  const needsGrid = !needs ? (
    <p>{t('ev.needs.soon', { d: fmtDate(ev.publish_date) })}</p>
  ) : (
    <div className="grid gap-3">
      {reg && needs.length > 0 && (
        <p className="m-0 text-secondary">
          {t('ev.limit', { n: limit })}</p>
      )}
      {needs.map((e) => (
        <NeedCardView key={e.employer_id} e={e} registered={!!reg}
                      interestCount={interestCount} limit={limit}
                      onToggleInterest={toggleInterest} />
      ))}
      {needs.length === 0 && <p>{t('ev.needs.none')}</p>}
    </div>
  )
  const needsList = <Section title={t('ev.needs')}>{needsGrid}</Section>

  const signinBlock = !user && (
    <div className="card p-4">
      <p className="mt-0">{t('ev.signin.cta')}</p>
      <div className="flex gap-2 flex-wrap">
        <Link to={`/sign-in?back=${encodeURIComponent(`/events/${id}`)}`}
              className="btn btn-primary">{t('nav.signin')}</Link>
        <Link to="/help" className="btn btn-secondary">{t('ev.advisor.help')}</Link>
      </div>
    </div>
  )

  /* ---- step 1: Register ---- */
  const registerBlock = (
    <div className="grid gap-4">
      {isResident && !reg && !choosingOpen && (
        <p className="text-secondary">{t('ev.register.closed')}</p>
      )}
      {isResident && !reg && choosingOpen && !showForm && (
        <button type="button" className="btn btn-primary" onClick={() => setShowForm(true)}>
          {t('ev.register')}
        </button>
      )}
      {isResident && !reg && choosingOpen && showForm && (
        <RegisterForm ev={ev} onDone={() => {
          setShowForm(false); setStep(1); load() }} />
      )}
      {isResident && reg && (
        <div className="card p-4 flex gap-3 items-center flex-wrap">
          <strong>{reg.status === 'waitlist' ? t('ev.waitlist') : t('ev.registered.summary')}</strong>
          <span className="text-secondary">
            {t('ev.timegroup')}: {ev.time_groups.find((g) => g.id === reg.time_group)?.entry ?? reg.time_group}
          </span>
          {choosingOpen && (
            <button type="button" className="btn btn-secondary"
                    onClick={async () => {
                      await api(`/api/events/${id}/register`, { method: 'DELETE' })
                      load()
                    }}>{t('ev.cancel')}</button>
          )}
        </div>
      )}
    </div>
  )

  /* ---- "Your choices (n/5)" panel, shown in steps 2 and 3 ---- */
  const choicesPanel = (my?.interests.length ?? 0) > 0 && (
    <Section title={t('ev.choices', { n: interestCount, m: limit })}>
      <ul className="grid gap-2 p-0 list-none">
        {my!.interests.map((i) => {
          const m = meetingOf.get(i.employer_id)
          const state = m
            ? t('ev.choice.match', { t: fmtTime(m.starts_at) })
            : matchingDone
            ? t(online ? 'ev.choice.nomatch.online' : 'ev.choice.nomatch')
            : t('ev.choice.waiting', {
                name: i.name, d: fmtDate(ev.matching_closes ?? '') })
          return (
            <li key={i.employer_id}
                className="card p-3 flex gap-3 items-center flex-wrap">
              <strong className="flex-1" style={{ minWidth: 140 }}>
                {i.name}</strong>
              <span className="text-secondary flex-1"
                    style={{ minWidth: 200 }}>{state}</span>
              {choosingOpen && !m && (
                <button type="button" className="btn btn-secondary"
                        onClick={() => takeBackByEmployer(i.employer_id)}>
                  {t('ev.notinterested')}</button>
              )}
            </li>
          )
        })}
      </ul>
    </Section>
  )

  /* ---- step 2: Choose ---- */
  const choose = !choosingOpen ? (
    <div className="grid gap-4">
      <p className="text-secondary">
        {t('ev.choose.closed', { d: fmtDate(ev.matching_closes ?? '') })}</p>
      {choicesPanel}
    </div>
  ) : needs ? (
    <div className="grid gap-4">
      {choicesPanel}
      <p className="m-0 text-secondary">{t('ev.limit', { n: limit })}</p>
      <CardChooser<NeedEntry>
        items={needs.filter((e) => !e.interested)}
        chosen={needs.filter((e) => e.interested)}
        idOf={(e) => e.employer_id}
        storageKey={`ev-choose-${id}-${user!.id}`}
        chosenCount={interestCount}
        limit={limit}
        chooseLabel={t('choose.meet')}
        skipLabel={t('choose.skip')}
        counter={(i, n) => t('choose.of', { i, n })}
        counterChosen={(a, b) => t('choose.chosen', { a, b })}
        listLabel={t('choose.list')}
        cardsLabel={t('choose.cards')}
        maxText={t('choose.max', { n: limit })}
        renderCard={(e) => (
          <NeedCardView e={e} registered
                        onMeetsChange={(m) => {
                          meetsRef.current[e.employer_id] = m }} />
        )}
        renderChosenRow={(e) => <>{e.employer_name}</>}
        onChoose={chooseInterest}
        onTakeBack={takeBackInterest}
        listView={needsGrid}
        match={(m, e) => ({
          title: t('match.title'),
          body: t('match.talent', {
            name: e.employer_name ?? '',
            d: fmtDate(m.starts_at.slice(0, 10)),
            t: fmtTime(m.starts_at),
            b: m.booth ?? e.booth ?? '' }) })}
      />
    </div>
  ) : needsList

  /* ---- step 3: Your plan ---- */
  const venueMap = !online && ev.employers.some((e) => e.booth) && (
    <Section title={t('map.title')}>
      <VenueMap
        booths={ev.employers.map((e) => ({
          id: e.employer_id, name: e.employer_name ?? '',
          booth: e.booth, logo_color: e.logo_color, field: e.field }))}
        route={meetings.filter((m) => meetingOf.has(m.employer_id))
          .map((m) => ({ employer_id: m.employer_id,
                         starts_at: m.starts_at }))} />
    </Section>
  )

  const plan = (
    <div className="grid gap-4">
      {choicesPanel}
      {my?.entry && reg && (
        <p className="m-0 font-medium card p-3">
          {online
            ? t('ev.plan.lobby', { t: my.entry })
            : t('ev.day.entry', { t: my.entry, g: reg.time_group })}
        </p>
      )}
      {meetings.length > 0 ? (
        <Section title={t('ev.plan.talks')}>
          <ul className="grid gap-3 p-0 list-none">
            {meetings.map((m) => (
              <li key={m.id} className="card p-4 grid gap-2">
                <div className="flex gap-2 items-center flex-wrap">
                  <strong>{fmtTime(m.starts_at)}</strong>
                  <span>— {m.employer_name}</span>
                  {m.booth &&
                    <span className="chip">{t('ev.booth')} {m.booth}</span>}
                  {m.video_url &&
                    <span className="chip">{t('ev.day.video')}</span>}
                </div>
                {m.first_week && m.first_week.length > 0 && (
                  <ul className="m-0 ps-5 text-secondary">
                    {m.first_week.map((f, i2) => <li key={i2}>{f}</li>)}
                  </ul>
                )}
                {m.must_haves && m.must_haves.length > 0 && (
                  <div>
                    <strong className="block">{t('ev.plan.prepare')}</strong>
                    <ul className="m-0 ps-5">
                      {m.must_haves.map((x, i2) => (
                        <li key={i2}>{t('ev.plan.example', { x })}</li>
                      ))}
                      {(m.bring ?? []).map((x, i2) => (
                        <li key={`b${i2}`}>{t('ev.plan.bring', { x })}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </Section>
      ) : (
        <p className="text-secondary">{t('ev.plan.none')}</p>
      )}
      {venueMap}
    </div>
  )

  /* ---- step 4: Event day (Now / Next) ---- */
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
  const slotMs = (ev.slot_minutes || 20) * 60000
  const upcoming = meetings.filter(
    (m) => m.status === 'booked' &&
           Date.parse(m.starts_at) + slotMs > now.getTime())
  const currentM = meetings.find(
    (m) => m.status === 'booked' &&
           Date.parse(m.starts_at) <= now.getTime() &&
           Date.parse(m.starts_at) + slotMs > now.getTime())
  const nextM = !currentM ? upcoming[0] : upcoming.find(
    (m) => Date.parse(m.starts_at) > now.getTime())
  const pastM = meetings.filter(
    (m) => m.status !== 'booked' ||
           Date.parse(m.starts_at) + slotMs <= now.getTime())

  const nowCard = currentM && (
    <div className="card p-4" style={{ borderColor: 'var(--color-yes)' }}>
      <strong className="block">{t('ev.day.now')}</strong>
      <p className="m-0 mt-1" style={{ fontSize: '1.15rem' }}>
        {fmtTime(currentM.starts_at)} — {currentM.employer_name}
        {currentM.booth ? ` · ${t('ev.booth')} ${currentM.booth}` : ''}
      </p>
      {currentM.video_url && (
        <a className="btn btn-primary mt-2" href={currentM.video_url}
           target="_blank" rel="noreferrer">
          {t('ev.day.join')}</a>
      )}
    </div>
  )
  const nextCard = !currentM && nextM && (
    <div className="card p-4" style={{ borderColor: 'var(--color-brand)' }}>
      <strong className="block">{t('ev.day.next')}</strong>
      <p className="m-0 mt-1" style={{ fontSize: '1.15rem' }}>
        {t('ev.day.in', {
          n: Math.max(0, Math.round(
            (Date.parse(nextM.starts_at) - now.getTime()) / 60000)) })}
        {' · '}
        {nextM.booth ? `${t('ev.booth')} ${nextM.booth} · ` : ''}
        {nextM.employer_name}
      </p>
      {nextM.video_url && (
        <a className={`btn mt-2 ${Date.parse(nextM.starts_at) - now.getTime() <= 5 * 60000 ? 'btn-primary' : 'btn-secondary'}`}
           href={nextM.video_url} target="_blank" rel="noreferrer"
           aria-disabled={Date.parse(nextM.starts_at) - now.getTime() > 5 * 60000}>
          {t('ev.day.join')}</a>
      )}
    </div>
  )

  const day = (
    <div className="grid gap-4">
      {nowCard}
      {nextCard}
      {!currentM && !nextM && meetings.length === 0 && (
        <p className="text-secondary">{t('ev.meetings.none')}</p>
      )}
      <PassInline eventId={id!} />
      <p className="m-0 text-secondary">{t('ev.day.passtext')}</p>
      <ScanBox eventId={id!} />
      {pastM.length > 0 && (
        <Section title={t('ev.day.done.list')}>
          <ul className="m-0 ps-5">
            {pastM.map((m) => (
              <li key={m.id}>
                {fmtTime(m.starts_at)} — {m.employer_name}
                <span className="text-secondary">
                  {' — '}
                  {t('ev.day.done', { d: fmtDate(ev.answers_due ?? '') })}
                </span>
              </li>
            ))}
          </ul>
        </Section>
      )}
      {!online && (
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
      )}
      {venueMap}
    </div>
  )

  /* ---- step 5: Answers ---- */
  const answersDue = ev.answers_due ? Date.parse(ev.answers_due) : 0
  const answers = (
    <div className="grid gap-4">
      <p className="m-0 text-secondary">{t('ev.answers.explain')}</p>
      {my && my.talks.length > 0 ? (
        <Section title={t('ev.talks')}>
          <ul className="grid gap-3 p-0 list-none">
            {my.talks.map((tk) => (
              <li key={tk.id} className="card p-4 grid gap-2">
                <div className="flex gap-2 items-center flex-wrap">
                  <strong>{tk.employer_name}</strong>
                  {tk.simulated &&
                    <span className="chip">{t('ev.simulated')}</span>}
                  {tk.status !== 'answered' && now.getTime() > answersDue &&
                    <span className="chip" style={{ borderColor: 'var(--color-no, #c00)', color: 'var(--color-no, #c00)' }}>{t('ev.answers.late')}</span>}
                </div>
                <span>
                  {tk.outcome
                    ? t(`ev.outcome.${tk.outcome}` as Key)
                    : t('ev.outcome.waiting')}
                </span>
                {tk.outcome === 'next_step' && tk.next_kind && (
                  <span className="block">
                    {t(`ev.nextkind.${tk.next_kind}` as Key)}
                    {tk.next_at ? ` — ${fmtDateTime(tk.next_at)}` : ''}
                    {tk.next_place ? ` · ${tk.next_place}` : ''}
                  </span>
                )}
                {tk.note &&
                  <span className="block text-secondary">{tk.note}</span>}
                {tk.observed && tk.observed.length > 0 && (
                  <ul className="m-0 ps-5 text-secondary">
                    {tk.observed.map((o, i2) => <li key={i2}>{o}</li>)}
                  </ul>
                )}
                {tk.outcome === 'next_step' && !tk.talent_response && (
                  <div className="grid gap-2">
                    <div className="flex gap-2 flex-wrap">
                      <button type="button" className="btn btn-primary"
                              onClick={() => respond(tk.id, 'confirmed')}>
                        {t('ev.answer.confirm')}</button>
                      <button type="button" className="btn btn-secondary"
                              onClick={() => setRespDlg(tk.id)}>
                        {t('ev.answer.othertime')}</button>
                    </div>
                    {respDlg === tk.id && (
                      <div className="card p-3 grid gap-2">
                        <input className="input" autoFocus
                               placeholder={t('ev.answer.note')}
                               value={respNote[tk.id] ?? ''}
                               onChange={(e) => setRespNote({
                                 ...respNote, [tk.id]: e.target.value })}
                               onKeyDown={(e) => {
                                 if (e.key === 'Escape') setRespDlg(null) }} />
                        <div className="flex gap-2">
                          <button type="button" className="btn btn-primary"
                                  onClick={() => respond(tk.id, 'other_time')}>
                            {t('ev.answer.othertime')}</button>
                          <button type="button" className="btn btn-secondary"
                                  onClick={() => setRespDlg(null)}>
                            {t('common.cancel')}</button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
                {tk.talent_response && (
                  <span className="text-secondary">
                    {tk.talent_response === 'confirmed'
                      ? t('ev.answer.confirmed')
                      : t('ev.answer.asked')}
                    {tk.talent_response_note
                      ? ` — ${tk.talent_response_note}` : ''}
                  </span>
                )}
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
    </div>
  )

  /* ---- stepper state (§9.3) ---- */
  const talksAnswered = my?.talks.filter((tk) => tk.outcome).length ?? 0
  const defaultStep = !reg ? 0
    : phase === 'registration' ? (interestCount >= limit ? 2 : 1)
    : phase === 'matched' ? 2
    : phase === 'live' ? 3
    : 4
  const active = step >= 0 ? step : defaultStep
  const opensDay = t('ev.step.opens', { d: fmtDate(ev.starts_at.slice(0, 10)) })
  const locked: (string | null)[] = [
    null,
    !reg ? t('ev.step.registerfirst') : null,
    !reg ? t('ev.step.registerfirst') : null,
    !reg ? t('ev.step.registerfirst')
         : phase === 'registration' || phase === 'matched' ? opensDay : null,
    !reg ? t('ev.step.registerfirst')
         : phase === 'registration' || phase === 'matched' ? opensDay : null,
  ]

  const next = !reg
    ? (choosingOpen
       ? { text: t('next.register'), btn: t('next.register.btn'), to: 0 }
       : { text: t('ev.register.closed'), btn: '', to: -1 })
    : phase === 'registration'
    ? { text: t('next.choose', { n: limit, c: interestCount }),
        btn: t('next.choose.btn'), to: 1 }
    : phase === 'matched'
    ? { text: t('next.plan', { n: meetings.length }),
        btn: t('next.plan.btn'), to: 2 }
    : phase === 'live'
    ? { text: t('next.meet', { n: meetings.length, d: fmtDate(ev.date) }),
        btn: t('next.meet.btn'), to: 3 }
    : { text: t('next.answers', { n: talksAnswered }),
        btn: t('next.answers.btn'), to: 4 }

  const about = (
    <details className="card p-4">
      <summary className="font-medium">{t('ev.about')}</summary>
      <div className="grid gap-6 mt-4">
        {programmeSection}
        {tilesSection}
        {!online && (
          <BoothPlan
            employers={ev.employers.map((e) => ({
              id: e.employer_id, name: e.employer_name ?? '',
              booth: e.booth, field: e.field, logo_color: e.logo_color }))}
            inPlan={new Set(my?.interests.map((i) => i.employer_id) ?? [])}
          />
        )}
      </div>
    </details>
  )

  const steps = [registerBlock, choose, plan, day, answers]

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

      {!isResident ? (
        <div className="grid gap-6">
          {ev.description && (
            <p className="max-w-prose">{ev.description}</p>)}
          {tilesSection}
          {needsList}
          {signinBlock}
          {user && <p className="text-secondary">{t('ev.resident.only')}</p>}
        </div>
      ) : (
        <>
          <Stepper label={t('ev.step.label')}
                   current={active}
                   doneBefore={defaultStep}
                   onSelect={setStep}
                   locked={locked}
                   steps={[t('ev.step.register'), t('ev.step.choose'),
                           t('ev.step.plan'), t('ev.step.day'),
                           t('ev.step.answers')]} />
          <div className="card p-4 flex gap-3 items-center flex-wrap"
               style={{ borderColor: 'var(--color-brand)' }}>
            <strong className="text-secondary uppercase"
                    style={{ fontSize: '.8rem', letterSpacing: '.04em' }}>
              {t('next.title')}</strong>
            <span className="flex-1" style={{ minWidth: 160 }}>
              {next.text}</span>
            {next.to >= 0 && (
              <button type="button" className="btn btn-primary"
                      onClick={() => setStep(next.to)}>
                {next.btn}</button>
            )}
          </div>
          {active === 0 && ev.description && (
            <p className="max-w-prose m-0">{ev.description}</p>)}
          {steps[active]}
          {about}
        </>
      )}
    </div>
  )
}
