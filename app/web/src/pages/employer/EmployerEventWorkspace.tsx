import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { useParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { fmtDate } from '../../lib/format'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { AnonTalentCard, EmployerDay, EmployerWorkspace, EventDetailData, EventTalk, Job, NeedCard } from '../../types'
import { ErrorBox, ErrorState, Section, Toggle } from '../../components/ui'
import Stepper from '../../components/Stepper'
import CardChooser from '../../components/CardChooser'
import type { Meeting } from '../../components/CardChooser'
import ScanBox from '../../components/ScanBox'
import EmployerEventPage from './EmployerEvent'

const CEFR_LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']
const LANGS = ['Finnish', 'Swedish', 'English', 'Russian', 'Arabic', 'Estonian',
  'Ukrainian', 'Somali', 'Persian', 'Albanian', 'Chinese']

export interface NeedCardDraft {
  first_week: string[]
  must_haves: { text: string; why: string }[]
  will_teach: string[]
  languages: { name: string; level: string; task: string }[]
  job_ids: string[]
}

export const EMPTY_NEED: NeedCardDraft = {
  first_week: [''], must_haves: [], will_teach: [''], languages: [], job_ids: [],
}

/** Shared need-card editor; used by the employer workspace and the advisor
    fill-in form (same fields, same wording check server-side). */
export function NeedCardForm({ draft, setDraft, onSubmit, busy, err, submitLabel, jobs }: {
  draft: NeedCardDraft
  setDraft: (d: NeedCardDraft) => void
  onSubmit: (e: FormEvent) => void
  busy: boolean; err: string; submitLabel: string
  jobs: Job[]
}) {
  const { t } = useI18n()
  const lines = (key: 'first_week' | 'will_teach', label: string) => (
    <label className="grid gap-1">
      <span className="font-medium">{label}</span>
      <textarea className="input" rows={4}
                value={draft[key].join('\n')}
                onChange={(e) => setDraft({
                  ...draft, [key]: e.target.value.split('\n'),
                })} />
      <span className="text-secondary">{t('ev.form.lines')}</span>
    </label>
  )
  return (
    <form onSubmit={onSubmit} className="grid gap-4">
      {lines('first_week', t('ev.form.firstweek'))}
      <fieldset className="border-0 p-0 m-0 grid gap-2">
        <legend className="font-medium">{t('ev.form.must')} ({draft.must_haves.length}/3)</legend>
        {draft.must_haves.map((m, i) => (
          <div key={i} className="grid gap-1 card p-3">
            <input className="input" placeholder={t('ev.form.must.text')} value={m.text}
                   onChange={(e) => setDraft({ ...draft, must_haves: draft.must_haves.map((x, j) => j === i ? { ...x, text: e.target.value } : x) })} />
            <input className="input" placeholder={t('ev.form.must.why')} value={m.why}
                   onChange={(e) => setDraft({ ...draft, must_haves: draft.must_haves.map((x, j) => j === i ? { ...x, why: e.target.value } : x) })} />
            <button type="button" className="btn btn-secondary justify-self-start"
                    onClick={() => setDraft({ ...draft, must_haves: draft.must_haves.filter((_, j) => j !== i) })}>
              {t('common.delete')}
            </button>
          </div>
        ))}
        {draft.must_haves.length < 3 && (
          <button type="button" className="btn btn-secondary justify-self-start"
                  onClick={() => setDraft({ ...draft, must_haves: [...draft.must_haves, { text: '', why: '' }] })}>
            {t('ev.form.must.add')}
          </button>
        )}
        <span className="text-secondary">{t('ev.form.must.hint')}</span>
      </fieldset>
      {lines('will_teach', t('ev.form.teach'))}
      <fieldset className="border-0 p-0 m-0 grid gap-2">
        <legend className="font-medium">{t('ev.form.langs')} ({draft.languages.length}/2)</legend>
        {draft.languages.map((l, i) => (
          <div key={i} className="flex gap-2 flex-wrap items-center">
            <select className="input" style={{ maxWidth: 180 }} value={l.name}
                    onChange={(e) => setDraft({ ...draft, languages: draft.languages.map((x, j) => j === i ? { ...x, name: e.target.value } : x) })}>
              {LANGS.map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
            <select className="input" style={{ maxWidth: 100 }} value={l.level}
                    onChange={(e) => setDraft({ ...draft, languages: draft.languages.map((x, j) => j === i ? { ...x, level: e.target.value } : x) })}>
              {CEFR_LEVELS.map((n) => <option key={n} value={n}>{n}</option>)}
            </select>
            <input className="input flex-1" placeholder={t('ev.form.lang.task')} value={l.task}
                   onChange={(e) => setDraft({ ...draft, languages: draft.languages.map((x, j) => j === i ? { ...x, task: e.target.value } : x) })} />
            <button type="button" className="btn btn-secondary"
                    onClick={() => setDraft({ ...draft, languages: draft.languages.filter((_, j) => j !== i) })}>
              {t('common.delete')}
            </button>
          </div>
        ))}
        {draft.languages.length < 2 && (
          <button type="button" className="btn btn-secondary justify-self-start"
                  onClick={() => setDraft({ ...draft, languages: [...draft.languages, { name: 'Finnish', level: 'A2', task: '' }] })}>
            {t('ev.form.lang.add')}
          </button>
        )}
      </fieldset>
      {jobs.length > 0 && (
        <fieldset className="border-0 p-0 m-0">
          <legend className="font-medium mb-1">{t('ev.form.jobs')}</legend>
          <div className="flex gap-2 flex-wrap">
            {jobs.map((j) => (
              <Toggle key={j.id} pressed={draft.job_ids.includes(j.id)}
                      onClick={() => setDraft({
                        ...draft,
                        job_ids: draft.job_ids.includes(j.id)
                          ? draft.job_ids.filter((x) => x !== j.id)
                          : [...draft.job_ids, j.id],
                      })}>
                {j.title}
              </Toggle>
            ))}
          </div>
        </fieldset>
      )}
      {err && <ErrorBox>{err}</ErrorBox>}
      <div><button className="btn btn-primary" disabled={busy}>{submitLabel}</button></div>
    </form>
  )
}

/** Read-only rendering of a need card (shared shape). */
export function NeedCardRead({ card }: { card: NeedCard }) {
  const { t } = useI18n()
  return (
    <div className="grid gap-2">
      {card.first_week.length > 0 && (
        <div><strong>{t('ev.firstweek')}</strong>
          <ul className="m-0 ps-5">{card.first_week.map((x, i) => <li key={i}>{x}</li>)}</ul></div>
      )}
      {card.must_haves.length > 0 && (
        <div><strong>{t('ev.must')}</strong>
          <ul className="m-0 ps-5">
            {card.must_haves.map((m, i) => (
              <li key={i}>{m.text}{m.why ? ` — ${m.why}` : ''}</li>
            ))}
          </ul></div>
      )}
      {card.languages.length > 0 && (
        <p className="m-0"><strong>{t('ev.langs')}</strong>{' '}
          {card.languages.map((l) => `${l.name} ${l.level}${l.task ? ` (${l.task})` : ''}`).join(', ')}</p>
      )}
      {card.will_teach.length > 0 && (
        <p className="m-0"><strong>{t('ev.teach')}</strong>{' '}{card.will_teach.join(' · ')}</p>
      )}
    </div>
  )
}

export function FitChip({ f }: { f: { key: string; [k: string]: unknown } }) {
  const { t } = useI18n()
  return (
    <span className="chip" style={{ background: 'var(--color-yes-bg)' }}>
      {t(`ev.efit.${f.key}` as Key, f as Record<string, string>)}
    </span>
  )
}

function CardTile({ c, onInvite, slotsLeft, districts, hideAction }: {
  c: AnonTalentCard; slotsLeft: boolean
  onInvite: (id: string) => void
  districts: { id: string; name: string }[]
  hideAction?: boolean
}) {
  const { t } = useI18n()
  return (
    <article className="card p-4 grid gap-2">
      <div className="flex gap-2 items-center flex-wrap">
        <strong>{t('ev.card.n', { n: c.id.split('-').pop() ?? c.id })}</strong>
        {c.district && (
          <span className="chip">{districts.find((d) => d.id === c.district)?.name ?? c.district}</span>
        )}
        {c.interested && (
          <span className="chip" style={{ background: 'var(--color-yes-bg)' }}>
            {t('ev.card.they')}
          </span>
        )}
      </div>
      <p className="m-0"><strong>{t('ev.card.wants')}</strong> {c.looking_for}</p>
      <ul className="m-0 ps-5">
        {c.done.map((d, i) => <li key={i}>{d.text}</li>)}
      </ul>
      {Object.keys(c.language_levels).length > 0 && (
        <p className="m-0 text-secondary">
          {Object.entries(c.language_levels).map(([n, l]) => `${n} ${l}`).join(', ')}
        </p>
      )}
      {c.credentials.length > 0 && (
        <p className="m-0"><strong>{t('ev.card.docs')}</strong> {c.credentials.join(', ')}</p>
      )}
      {c.fit && c.fit.length > 0 && (
        <div className="flex gap-2 flex-wrap">{c.fit.map((f, i) => <FitChip key={i} f={f} />)}</div>
      )}
      {(c.kudos ?? []).length > 0 && (
        <div className="flex gap-2 flex-wrap">
          {c.kudos!.map((k) => (
            <span key={k.label} className="chip">
              {t(`badge.${k.label}` as Key)}{k.count > 1 ? ` ×${k.count}` : ''}
            </span>
          ))}
        </div>
      )}
      {!hideAction && (
        <div>
          {c.invited ? (
            <span className="font-medium" style={{ color: 'var(--color-brand)' }}>
              {t('ev.card.invited')}
            </span>
          ) : slotsLeft ? (
            <button type="button" className="btn btn-primary" onClick={() => onInvite(c.id)}>
              {t('ev.card.invite')}
            </button>
          ) : (
            <span className="text-secondary">{t('ev.card.full')}</span>
          )}
        </div>
      )}
    </article>
  )
}

function fmtTime(iso: string) {
  return iso.includes('T') ? iso.split('T')[1].slice(0, 5) : iso
}

function BoothDay({ id, firstWeek }: { id: string; firstWeek: string[] }) {
  const { t } = useI18n()
  const [day, setDay] = useState<EmployerDay | null>(null)
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [observed, setObserved] = useState<Set<string>>(new Set())
  const [note, setNote] = useState('')
  const [outcome, setOutcome] = useState<'next_step' | 'not_now'>('next_step')
  const [err, setErr] = useState('')

  const load = () => api<EmployerDay>(`/api/employer/events/${id}/day`)
    .then(setDay).catch(() => setDay(null))
  useEffect(() => { load() }, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (!day) return <p>{t('common.loading')}</p>
  const next = day.meetings.find((m) => m.status === 'booked')
  const nc = day.next_card

  const reveal = async () => {
    setErr('')
    try {
      const r = await api<{ name: string }>(
        `/api/employer/events/${id}/reveal`, { body: { code } })
      setName(r.name)
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }
  const saveTalk = async (e: FormEvent) => {
    e.preventDefault()
    if (!next) return
    setErr('')
    try {
      await api(`/api/employer/events/${id}/meetings/${next.id}/talk`,
        { body: { observed: [...observed], outcome,
                  employer_note: note } })
      setObserved(new Set()); setNote(''); setName(''); setCode('')
      load()
    } catch (e2) {
      setErr(e2 instanceof ApiError ? e2.message : t('common.error'))
    }
  }
  const noShow = async () => {
    if (!next) return
    await api(`/api/employer/events/${id}/meetings/${next.id}/no-show`,
              { method: 'POST' })
    load()
  }
  const callNext = async () => {
    try {
      await api(`/api/employer/events/${id}/queue/call-next`,
                { method: 'POST' })
      load()
    } catch (e) { alert(e instanceof ApiError ? e.message : t('common.error')) }
  }

  return (
    <div className="grid gap-4">
      <ScanBox eventId={id} allowVisitorCode />
      {day.booth && (
        <p className="m-0 font-medium">{t('ev.booth')} {day.booth}</p>
      )}
      <Section title={t('ev.meetings')}>
        {day.meetings.length === 0 ? <p>{t('ev.meetings.none')}</p> : (
          <ul className="m-0 ps-5">
            {day.meetings.map((m) => (
              <li key={m.id}>
                <strong>{fmtTime(m.starts_at)}</strong>
                {' — '}{t(`ev.day.st.${m.status}` as Key)}
                {name && m.id === next?.id && ` — ${name}`}
              </li>
            ))}
          </ul>
        )}
      </Section>
      {next && nc && (
        <Section title={t('ev.emp.day.next')}>
          <p className="text-secondary mt-0">{t('ev.emp.day.shown')}</p>
          <article className="card p-4 grid gap-2">
            <strong>{t('ev.card.n', {
              n: nc.id.split('-').pop() ?? nc.id })}</strong>
            <p className="m-0"><strong>{t('ev.card.wants')}</strong>{' '}
              {nc.looking_for}</p>
            <ul className="m-0 ps-5">
              {nc.done.map((d, i) => <li key={i}>{d.text}</li>)}
            </ul>
            {nc.fit && nc.fit.length > 0 && (
              <div className="flex gap-2 flex-wrap">
                {nc.fit.map((f, i) => <FitChip key={i} f={f} />)}
              </div>
            )}
          </article>
          {name ? (
            <p className="font-medium">{t('ev.emp.day.name', { n: name })}</p>
          ) : (
            <div className="flex gap-2 flex-wrap items-center">
              <label className="grid gap-1">
                <span>{t('ev.emp.day.code')}</span>
                <input className="input" value={code} inputMode="numeric"
                       maxLength={4} style={{ width: '7rem' }}
                       onChange={(e) => setCode(e.target.value)} />
              </label>
              <button type="button" className="btn btn-secondary self-end"
                      onClick={reveal}>{t('ev.emp.day.reveal')}</button>
            </div>
          )}
          <form onSubmit={saveTalk} className="grid gap-3">
            <fieldset className="grid gap-2 border-0 p-0 m-0">
              <legend className="font-medium">{t('ev.emp.day.saw')}</legend>
              {firstWeek.map((w) => (
                <label key={w} className="flex gap-2 items-start">
                  <input type="checkbox" checked={observed.has(w)}
                         onChange={(e) => {
                           const n = new Set(observed)
                           if (e.target.checked) n.add(w); else n.delete(w)
                           setObserved(n)
                         }} />
                  <span>{w}</span>
                </label>
              ))}
            </fieldset>
            <label className="grid gap-1">
              <span>{t('ev.emp.day.note')}</span>
              <textarea className="input" rows={2} required value={note}
                        onChange={(e) => setNote(e.target.value)} />
            </label>
            <div className="flex gap-2 flex-wrap">
              <Toggle pressed={outcome === 'next_step'}
                      onClick={() => setOutcome('next_step')}>
                {t('ev.outcome.next_step')}
              </Toggle>
              <Toggle pressed={outcome === 'not_now'}
                      onClick={() => setOutcome('not_now')}>
                {t('ev.outcome.not_now')}
              </Toggle>
            </div>
            {err && <ErrorBox>{err}</ErrorBox>}
            <div className="flex gap-2 flex-wrap">
              <button type="submit" className="btn btn-primary">
                {t('ev.emp.day.send')}
              </button>
              <button type="button" className="btn btn-secondary"
                      onClick={noShow}>{t('ev.emp.day.noshow')}</button>
            </div>
          </form>
        </Section>
      )}
      <Section title={t('ev.emp.day.queue')}>
        {day.queue.length === 0 ? (
          <p className="text-secondary">{t('ev.emp.day.queue.empty')}</p>
        ) : (
          <p className="m-0">
            {t('ev.emp.day.queue.n', { n: day.queue.length })}
          </p>
        )}
        <button type="button" className="btn btn-secondary"
                disabled={day.queue.length === 0} onClick={callNext}>
          {t('ev.emp.day.call')}
        </button>
      </Section>
    </div>
  )
}

function AfterTalks({ talks, onDone }: {
  talks: EventTalk[]; onDone: () => void
}) {
  const { t } = useI18n()
  const [note, setNote] = useState<Record<string, string>>({})
  const [out, setOut] = useState<Record<string, string>>({})
  const waiting = talks.filter((tk) => tk.status === 'talked')
  const answered = talks.filter((tk) => tk.status === 'answered')
  if (talks.length === 0) {
    return <p className="text-secondary">{t('ev.talks.none')}</p>
  }
  const answer = async (tk: EventTalk) => {
    try {
      await api(`/api/employer/event/talks/${tk.id}/answer`, {
        body: { outcome: out[tk.id] ?? 'next_step',
                employer_note: note[tk.id] ?? '' } })
      onDone()
    } catch (e) { alert(e instanceof ApiError ? e.message : t('common.error')) }
  }
  return (
    <div className="grid gap-3">
      {waiting.length > 0 && (
        <Section title={t('ev.emp.after.waiting')}>
          <ul className="grid gap-3 p-0 list-none">
            {waiting.map((tk) => (
              <li key={tk.id} className="card p-3 grid gap-2">
                <strong>{tk.person_name ?? tk.employer_name ?? tk.id}</strong>
                <span className="text-secondary">
                  {t('ev.waitdays', { n: tk.days_waiting ?? 0 })}
                </span>
                <div className="flex gap-2 flex-wrap">
                  <Toggle pressed={(out[tk.id] ?? 'next_step') === 'next_step'}
                          onClick={() => setOut({ ...out, [tk.id]: 'next_step' })}>
                    {t('ev.outcome.next_step')}
                  </Toggle>
                  <Toggle pressed={out[tk.id] === 'not_now'}
                          onClick={() => setOut({ ...out, [tk.id]: 'not_now' })}>
                    {t('ev.outcome.not_now')}
                  </Toggle>
                </div>
                <input className="input" required
                       placeholder={t('ev.emp.day.note')}
                       value={note[tk.id] ?? ''}
                       onChange={(e) => setNote({ ...note, [tk.id]: e.target.value })} />
                <button type="button" className="btn btn-primary"
                        disabled={!(note[tk.id] ?? '').trim()}
                        onClick={() => answer(tk)}>
                  {t('ev.emp.day.send')}
                </button>
              </li>
            ))}
          </ul>
        </Section>
      )}
      {answered.length > 0 && (
        <Section title={t('ev.talks')}>
          <ul className="grid gap-2 p-0 list-none">
            {answered.map((tk) => (
              <li key={tk.id} className="card p-3">
                <strong>{tk.person_name ?? tk.id}</strong>
                <span className="block">
                  {tk.outcome ? t(`ev.outcome.${tk.outcome}` as Key) : ''}
                </span>
                {tk.employer_note && (
                  <span className="block text-secondary">{tk.employer_note}</span>
                )}
              </li>
            ))}
          </ul>
        </Section>
      )}
    </div>
  )
}

export default function EmployerEventWorkspace() {
  const { id } = useParams()
  const { t, lang } = useI18n()
  const [ws, setWs] = useState<EmployerWorkspace | null>(null)
  const [cards, setCards] = useState<AnonTalentCard[] | null>(null)
  const [allCards, setAllCards] = useState(false)
  const [jobs, setJobs] = useState<Job[]>([])
  const [districts, setDistricts] = useState<{ id: string; name: string }[]>([])
  const [err, setErr] = useState<unknown>(null)
  const [editing, setEditing] = useState(false)
  const [draft, setDraft] = useState<NeedCardDraft>(EMPTY_NEED)
  const [busy, setBusy] = useState(false)
  const [formErr, setFormErr] = useState('')
  const [step, setStep] = useState(-1)
  const [evFull, setEvFull] = useState<EventDetailData | null>(null)

  const load = () => {
    setErr(null)
    api<EmployerWorkspace>(`/api/employer/events/${id}`).then(setWs).catch(setErr)
  }
  useEffect(load, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    if (!ws?.joined) return
    api<{ cards: AnonTalentCard[] }>(
      `/api/employer/events/${id}/cards${allCards ? '?all=1' : ''}`)
      .then((d) => setCards(d.cards)).catch(() => setCards(null))
  }, [id, ws?.joined, allCards])
  useEffect(() => {
    api<{ jobs: Job[] }>('/api/employer/jobs')
      .then((d) => setJobs(d.jobs.filter((j) => j.status === 'open'))).catch(() => {})
    api<{ districts: { id: string; name: string }[] }>('/api/catalog')
      .then((c) => setDistricts(c.districts)).catch(() => {})
    api<EventDetailData>(`/api/events/${id}`)
      .then(setEvFull).catch(() => {})
  }, [id])

  if (err) return <ErrorState err={err} goneLabel={t('ev.gone')} retryLabel={t('err.retry')} onRetry={load} backTo="/employer" backLabel={t('common.back')} />
  if (!ws) return <p>{t('common.loading')}</p>
  const ev = ws.event

  const join = async () => {
    try {
      await api(`/api/employer/events/${id}`, { method: 'PUT' })
      load()
    } catch (e) { alert(e instanceof ApiError ? e.message : t('common.error')) }
  }

  const submitNeed = async (e: FormEvent) => {
    e.preventDefault()
    setFormErr(''); setBusy(true)
    try {
      const card = {
        first_week: draft.first_week.map((x) => x.trim()).filter(Boolean),
        must_haves: draft.must_haves.filter((m) => m.text.trim()),
        will_teach: draft.will_teach.map((x) => x.trim()).filter(Boolean),
        languages: draft.languages,
        job_ids: draft.job_ids,
      }
      await api(`/api/employer/events/${id}/need`, { method: 'PUT', body: card })
      setEditing(false); load()
    } catch (e2) {
      setFormErr(e2 instanceof ApiError ? e2.message : t('common.error'))
    } finally { setBusy(false) }
  }

  const invite = async (registrationId: string) => {
    try {
      const r = await api<{ meeting?: Meeting | null }>(
        `/api/employer/events/${id}/invites`,
        { body: { registration_id: registrationId } })
      const d = await api<{ cards: AnonTalentCard[] }>(
        `/api/employer/events/${id}/cards${allCards ? '?all=1' : ''}`)
      setCards(d.cards); load()
      return r
    } catch (e) {
      alert(e instanceof ApiError ? e.message : t('common.error'))
      return {}
    }
  }

  const slotsLeft = (ws.invites_used ?? 0) < (ws.slots ?? 0)

  const joinBlock = !ws.joined && (
    <div className="card p-4">
      <p className="mt-0">{t('ev.emp.join')}</p>
      <button type="button" className="btn btn-primary" onClick={join}>
        {t('ev.emp.join.btn')}
      </button>
    </div>
  )

  const needStep = !ws.joined ? joinBlock : (
    <Section title={t('ev.emp.need')}>
      {ev.need_deadline && (
        <p className="text-secondary">
          {t('ev.emp.deadline', {
            d: fmtDate(ev.need_deadline, lang),
            n: Math.max(0, Math.round(
              (Date.parse(ev.need_deadline) - Date.now()) / 86400000)),
          })}
        </p>
      )}
      {ws.need && !editing ? (
        <div className="card p-4 grid gap-2">
          <NeedCardRead card={ws.need.card} />
          <p className="text-secondary m-0">
            {ws.need.need_by === 'advisor' ? t('ev.byadvisor') + ' · ' : ''}
            {t('ev.emp.sent', { d: fmtDate(ws.need.submitted_at, lang) })}
          </p>
          <button type="button" className="btn btn-secondary justify-self-start"
                  onClick={() => {
                    setDraft({
                      first_week: ws.need!.card.first_week,
                      must_haves: ws.need!.card.must_haves,
                      will_teach: ws.need!.card.will_teach,
                      languages: ws.need!.card.languages,
                      job_ids: ws.need!.card.job_ids,
                    })
                    setEditing(true)
                  }}>{t('common.edit')}</button>
        </div>
      ) : (
        <NeedCardForm draft={draft} setDraft={setDraft} onSubmit={submitNeed}
                      busy={busy} err={formErr} jobs={jobs}
                      submitLabel={t('ev.emp.need.send')} />
      )}
    </Section>
  )

  const cardsList = !cards ? <p>{t('common.loading')}</p> : (
    <div className="grid gap-3">
      {cards.map((c) => (
        <CardTile key={c.id} c={c} slotsLeft={slotsLeft}
                  onInvite={(cid) => { void invite(cid) }}
                  districts={districts} />
      ))}
      {cards.length === 0 && <p>{t('ev.emp.cards.none')}</p>}
    </div>
  )

  const chooseStep = !ws.joined ? joinBlock : (
    <Section title={t('ev.emp.cards')}>
      <div className="flex gap-3 items-center mb-3 flex-wrap">
        <span>{t('ev.emp.cards.count', { n: cards?.length ?? 0 })}</span>
        <Toggle pressed={allCards} onClick={() => setAllCards(!allCards)}>
          {t('ev.emp.cards.all')}
        </Toggle>
      </div>
      {!cards ? <p>{t('common.loading')}</p> : (
        <CardChooser<AnonTalentCard>
          items={cards.filter((c) => !c.invited)}
          chosen={cards.filter((c) => c.invited)}
          idOf={(c) => c.id}
          storageKey={`emp-choose-${id}-${allCards ? 'all' : 'chose'}`}
          chosenCount={ws.invites_used ?? 0}
          limit={ws.slots ?? 0}
          chooseLabel={t('choose.invite')}
          skipLabel={t('choose.skip')}
          counter={(i, n) => t('choose.of', { i, n })}
          counterChosen={(a, b) => t('choose.invites', { a, b })}
          listLabel={t('choose.list')}
          cardsLabel={t('choose.cards')}
          maxText={t('choose.max.emp', { n: ws.slots ?? 0 })}
          renderCard={(c) => (
            <CardTile c={c} slotsLeft={slotsLeft} hideAction
                      onInvite={(cid) => { void invite(cid) }}
                      districts={districts} />
          )}
          renderChosenRow={(c) => (
            <>{t('ev.card.n', { n: c.id.split('-').pop() ?? c.id })}</>
          )}
          onChoose={(c) => invite(c.id)}
          listView={cardsList}
          match={(m, c) => ({
            title: t('match.title'),
            body: t('match.emp', {
              name: t('ev.card.n', { n: c.id.split('-').pop() ?? c.id }),
              t: fmtTime(m.starts_at) }) })}
        />
      )}
    </Section>
  )

  const day = id === 'ev-2026-11' ? <EmployerEventPage /> : (
    <BoothDay id={id!}
              firstWeek={ws.need?.card.first_week ?? []} />
  )

  const after = id === 'ev-2026-11' ? <EmployerEventPage /> : (
    <AfterTalks talks={ws.talks ?? []} onDone={load} />
  )

  // §8.1 employer defaults + §8.2 next step
  const unanswered = (ws.talks ?? []).filter((tk) => !tk.outcome).length
  const defaultStep = !ws.joined || !ws.need ? 0
    : ev.phase === 'finished' ? 3
    : ev.phase === 'today' ? 2 : 1
  const active = step >= 0 ? step : defaultStep
  const invitesLeft = Math.max(0, (ws.slots ?? 0) - (ws.invites_used ?? 0))
  const next = !ws.joined
    ? { text: t('ev.emp.join'), btn: t('ev.emp.join.btn'), to: 0 }
    : !ws.need
    ? { text: t('next.emp.need'), btn: t('next.emp.need.btn'), to: 0 }
    : ev.phase === 'finished'
    ? { text: t('next.emp.answer', { n: unanswered }),
        btn: t('next.emp.answer.btn'), to: 3 }
    : ev.phase === 'today'
    ? { text: t('next.emp.meet'), btn: t('emp.step.meet'), to: 2 }
    : { text: t('next.emp.choose', { n: invitesLeft }),
        btn: t('next.emp.choose.btn'), to: 1 }

  const about = evFull && (
    <details className="card p-4">
      <summary className="font-medium">{t('ev.about')}</summary>
      <div className="grid gap-4 mt-4">
        {evFull.programme.length > 0 && (
          <Section title={t('ev.programme')}>
            <ul className="m-0 ps-5">
              {evFull.programme.map((p, i) => (
                <li key={i}>
                  {fmtTime(p.start)}{p.end ? `–${fmtTime(p.end)}` : ''} — {p.title || t(`ev.prog.${p.kind}` as Key)}
                </li>
              ))}
            </ul>
          </Section>
        )}
        <Section title={t('ev.employers.title', { n: evFull.employers.length })}>
          <ul className="m-0 ps-5">
            {evFull.employers.map((e) => (
              <li key={e.employer_id}>
                {e.employer_name}{e.booth ? ` (${t('ev.booth')} ${e.booth})` : ''}
              </li>
            ))}
          </ul>
        </Section>
      </div>
    </details>
  )

  const steps = [needStep, chooseStep, day, after]

  return (
    <div className="grid gap-4">
      <div>
        <h1 data-page-title tabIndex={-1} className="mb-1">{ev.name}</h1>
        <p className="m-0">{fmtDate(ev.date, lang)} · {ev.venue}</p>
        {ws.booth && <p className="m-0 text-secondary">{t('ev.booth')} {ws.booth}</p>}
      </div>
      <Stepper label={t('ev.step.label')}
               current={active}
               doneBefore={defaultStep}
               onSelect={setStep}
               steps={[t('emp.step.need'), t('emp.step.choose'),
                       t('emp.step.meet'), t('emp.step.answer')]} />
      <div className="card p-4 flex gap-3 items-center flex-wrap"
           style={{ borderColor: 'var(--color-brand)' }}>
        <strong className="text-secondary uppercase"
                style={{ fontSize: '.8rem', letterSpacing: '.04em' }}>
          {t('next.title')}</strong>
        <span className="flex-1" style={{ minWidth: 160 }}>{next.text}</span>
        <button type="button" className="btn btn-primary"
                onClick={() => setStep(next.to)}>
          {next.btn}</button>
      </div>
      {steps[active]}
      {about}
    </div>
  )
}
