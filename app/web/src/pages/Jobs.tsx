import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useConfig } from '../lib/config'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Catalog, EventInfo, FiltersReply, Job, Profile } from '../types'
import { CEFR, DAYS, PARTS } from '../types'
import JobRow, { labelText } from '../components/JobRow'
import JobMap from '../components/JobMap'
import { ErrorState, Field, HelpCard, Toggle } from '../components/ui'
import VoiceInput from '../components/VoiceInput'
import { districtName, fmtDate, slotsText } from '../lib/format'
import { CalendarDays, ChevronDown, LifeBuoy, SlidersHorizontal } from 'lucide-react'

const QUICK_LABELS = ['students', 'retirement', 'first_job', 'side_job',
                      'part_time', 'access_info'] as const
const QUICK_NEEDS = ['step_free_entrance', 'seated_work', 'flexible_breaks',
                     'quiet_environment']
const WEEKDAYS = DAYS.slice(0, 5)
const TIME_GROUPS: { id: Key; slots: string[] }[] = [
  { id: 'jobs.time.mornings', slots: WEEKDAYS.map((d) => `${d}-morning`) },
  { id: 'jobs.time.daytime', slots: WEEKDAYS.map((d) => `${d}-afternoon`) },
  { id: 'jobs.time.evenings', slots: [...WEEKDAYS.map((d) => `${d}-evening`),
    ...['sat', 'sun'].flatMap((d) => PARTS.map((p) => `${d}-${p}`))] },
]

export default function JobsPage({
  rowActions, headerExtra,
}: {
  rowActions?: (j: Job) => ReactNode
  headerExtra?: ReactNode
}) {
  const { t, lang } = useI18n()
  const { user } = useAuth()
  const cfg = useConfig()
  const [cat, setCat] = useState<Catalog | null>(null)
  const [params, setParams] = useSearchParams()
  const [jobs, setJobs] = useState<Job[] | null>(null)
  const [count, setCount] = useState(0)
  const [err, setErr] = useState<unknown>(null)
  const [view, setView] = useState<'list' | 'map'>('list')
  const [more, setMore] = useState(false)
  const [fitOpen, setFitOpen] = useState(() => window.matchMedia('(min-width: 768px)').matches
    || ['district', 'commute_max', 'needs'].some((k) => !!params.get(k)))
  const [selected, setSelected] = useState<string | null>(null)
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set())
  const [askText, setAskText] = useState('')
  const [askReply, setAskReply] = useState<FiltersReply | null>(null)
  const [askBusy, setAskBusy] = useState(false)
  const [profileDistrict, setProfileDistrict] = useState<string | null>(null)
  const [profileNeeds, setProfileNeeds] = useState<string[]>([])
  const [event, setEvent] = useState<EventInfo | null>(null)
  const [upcoming, setUpcoming] = useState(false)
  const prefilled = useRef(false)
  const home = !rowActions && !headerExtra

  useEffect(() => {
    if (!home) return
    api<EventInfo>('/api/event').then((r) => {
      setEvent(r)
      setUpcoming(!!r.event && r.event.date >= new Date().toISOString().slice(0, 10))
    }).catch(() => {})
  }, [home])

  useEffect(() => {
    api<Catalog>('/api/catalog').then(setCat).catch(() => {})
  }, [])

  // commute origin (§5): the district filter wins, else the resident's
  // own profile district — no sign-in needed for the filter path
  useEffect(() => {
    if (user?.role !== 'resident') { setProfileDistrict(null); setProfileNeeds([]); return }
    api<Profile>('/api/me/profile').then((p) => {
      setProfileDistrict(p.district)
      setProfileNeeds(p.needs)
      // the person's own needs are preselected once, in the mode that
      // only hides jobs where the answer is a clear "no"
      const once = `ewm.needsPrefilled.${user.id}`
      if (prefilled.current || !p.needs.length || sessionStorage.getItem(once)) return
      prefilled.current = true
      sessionStorage.setItem(once, '1')
      setParams((cur) => {
        if (cur.get('needs')) return cur
        const np = new URLSearchParams(cur)
        np.set('needs', p.needs.join(','))
        np.set('needs_mode', 'not_no')
        return np
      }, { replace: true })
    }).catch(() => undefined)
  }, [user, setParams])
  const originDistrict = params.get('district') || profileDistrict || undefined
  const originName = cat && originDistrict
    ? districtName(originDistrict, cat.districts) : undefined

  const qs = params.toString()
  const load = () => {
    setErr(null)
    api<{ jobs: Job[]; count: number }>(`/api/jobs?${qs}`)
      .then((r) => { setJobs(r.jobs); setCount(r.count) })
      .catch((e) => { setErr(e); setJobs([]) })
  }
  useEffect(load, [qs])

  useEffect(() => {
    if (user?.role !== 'resident') return
    api<{ jobs: { id: string }[] }>('/api/me/saved')
      .then((r) => setSavedIds(new Set(r.jobs.map((j) => j.id))))
      .catch(() => {})
  }, [user])

  const toggleSave = async (j: Job) => {
    try {
      if (savedIds.has(j.id)) {
        await api(`/api/me/saved/${j.id}`, { method: 'DELETE' })
        setSavedIds((s) => { const n = new Set(s); n.delete(j.id); return n })
      } else {
        await api(`/api/me/saved/${j.id}`, { method: 'PUT' })
        setSavedIds((s) => new Set(s).add(j.id))
      }
    } catch { /* leave state as-is */ }
  }

  const set = (k: string, v: string | null) => {
    const p = new URLSearchParams(params)
    if (v == null || v === '') p.delete(k); else p.set(k, v)
    setParams(p, { replace: false })
  }
  const toggleLabel = (id: string) => {
    const cur = params.getAll('label')
    const p = new URLSearchParams(params)
    p.delete('label')
    ;(cur.includes(id) ? cur.filter((l) => l !== id) : [...cur, id])
      .forEach((l) => p.append('label', l))
    setParams(p)
  }
  const slotSet = new Set((params.get('slots') || '').split(',').filter(Boolean))
  const toggleSlot = (slot: string) => {
    const s = new Set(slotSet)
    if (s.has(slot)) s.delete(slot); else s.add(slot)
    set('slots', [...s].join(',') || null)
  }
  const toggleGroup = (slots: string[]) => {
    const s = new Set(slotSet)
    const on = slots.every((x) => s.has(x))
    slots.forEach((x) => { if (on) s.delete(x); else s.add(x) })
    set('slots', [...s].join(',') || null)
  }
  const pickCommute = (m: number) => {
    const p = new URLSearchParams(params)
    if (params.get('commute_max') === String(m)) p.delete('commute_max')
    else {
      p.set('commute_max', String(m))
      if (!p.get('district') && profileDistrict) p.set('district', profileDistrict)
    }
    setParams(p)
  }
  const needKeys = (params.get('needs') || '').split(',').filter(Boolean)
  const quickNeeds = [...new Set([...QUICK_NEEDS, ...profileNeeds, ...needKeys])]
  const toggleNeed = (k: string) => {
    const s = new Set(needKeys)
    if (s.has(k)) s.delete(k); else s.add(k)
    set('needs', [...s].join(',') || null)
  }
  const clearAll = () => setParams(new URLSearchParams())

  const useMyProfile = async () => {
    if (!user) return
    const p = await api<Profile>('/api/me/profile')
    const np = new URLSearchParams(params)
    if (p.availability.length) np.set('slots', p.availability.join(','))
    if (p.max_hours_per_week) np.set('hours_max', String(p.max_hours_per_week))
    if (p.needs.length) { np.set('needs', p.needs.join(',')); np.set('needs_mode', 'not_no') }
    if (p.district) np.set('district', p.district)
    setParams(np)
  }

  // "Tell us what you are looking for" — free text -> filters (§2)
  const askFilters = async () => {
    if (!askText.trim()) return
    setAskBusy(true); setAskReply(null)
    try {
      const r = await api<FiltersReply>('/api/ai/filters', {
        body: { text: askText.trim().slice(0, 600), ui_language: lang },
      })
      setAskReply(r)
      const p = new URLSearchParams()
      const f = r.filters as Record<string, unknown>
      ;(f.labels as string[] | undefined)?.forEach((l) => p.append('label', l))
      for (const k of ['field', 'work_mode', 'district', 'experience',
                       'level_max', 'language', 'pay_unit'] as const) {
        if (f[k] != null) p.set(k, String(f[k]))
      }
      if (Array.isArray(f.slots) && f.slots.length) p.set('slots', (f.slots as string[]).join(','))
      if (Array.isArray(f.needs) && f.needs.length) {
        p.set('needs', (f.needs as string[]).join(','))
        p.set('needs_mode', 'yes')
      }
      for (const k of ['hours_max', 'pay_min', 'km', 'commute_max'] as const) {
        if (typeof f[k] === 'number') p.set(k, String(f[k]))
      }
      if (f.near_station === true) p.set('near_station', '1')
      setParams(p)
    } catch { setAskReply(null) } finally { setAskBusy(false) }
  }

  const activeFilterNames = useMemo(() => {
    const names: { key: string; name: string }[] = []
    params.getAll('label').forEach((l) =>
      names.push({ key: `label:${l}`, name: labelText(l, t) }))
    if (params.get('field'))
      names.push({ key: 'field', name: t(`field.${params.get('field')}` as Key) })
    if (params.get('slots'))
      names.push({ key: 'slots', name: slotsText(params.get('slots')!.split(','), t) })
    if (params.get('hours_max'))
      names.push({ key: 'hours_max', name: `≤${params.get('hours_max')} ${t('common.hweek')}` })
    if (params.get('pay_min'))
      names.push({ key: 'pay_min', name: `≥€${params.get('pay_min')}${t('common.perhour')}` })
    if (params.get('contract'))
      names.push({ key: 'contract', name: t(`contract.${params.get('contract')}` as Key) })
    if (params.get('experience'))
      names.push({ key: 'experience', name: t(`experience.${params.get('experience')}` as Key) })
    if (params.get('language'))
      names.push({ key: 'language', name: params.get('language')! })
    if (params.get('needs')) names.push({ key: 'needs', name: t('jobs.needs') })
    if (params.get('district'))
      names.push({ key: 'district', name: cat ? districtName(params.get('district')!, cat.districts) : params.get('district')! })
    if (params.get('at_event')) names.push({ key: 'at_event', name: t('jobs.atevent') })
    if (params.get('near_station')) names.push({ key: 'near_station', name: t('jobs.nearstation') })
    if (params.get('commute_max'))
      names.push({ key: 'commute_max',
                   name: t('jobs.commute.chip',
                           { m: params.get('commute_max')! }) })
    if (params.get('q')) names.push({ key: 'q', name: `"${params.get('q')}"` })
    if (params.get('work_mode'))
      names.push({ key: 'work_mode', name: t(`common.${params.get('work_mode') === 'on_site' ? 'onsite' : params.get('work_mode')}` as Key) })
    return names
  }, [params, t, cat])

  const removeFilter = (k: string) => {
    const p = new URLSearchParams(params)
    if (k.startsWith('label:')) {
      p.delete('label')
      params.getAll('label').filter((l) => `label:${l}` !== k)
        .forEach((l) => p.append('label', l))
    } else {
      p.delete(k)
      if (k === 'needs') p.delete('needs_mode')
    }
    setParams(p)
  }

  const selectedJob = jobs?.find((j) => j.id === selected)
  const showOnMap = (id: string) => {
    setSelected(id)
    setView('map')
    document.getElementById('map-panel')?.scrollIntoView({ block: 'nearest' })
  }
  const onSelectMarker = (id: string) => {
    setSelected(id)
    document.getElementById(`job-row-${id}`)
      ?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }

  const ev = event?.event

  if (err && jobs !== null) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }

  return (
    <div>
      <div className="flex items-baseline justify-between gap-3 flex-wrap mb-4">
        <h1 data-page-title tabIndex={-1} className="m-0">{t('jobs.title')}</h1>
        <div className="flex items-center gap-3">
          <span role="status" aria-live="polite" className="text-secondary">
            {jobs == null ? t('common.loading') : `${count} ${t('jobs.found')}`}
          </span>
          {headerExtra}
          <div role="group" aria-label="List or map"
               className="flex card overflow-hidden lg:hidden">
            {(['list', 'map'] as const).map((v) => (
              <button key={v} type="button" aria-pressed={view === v}
                      onClick={() => setView(v)}
                      style={{
                        minHeight: 44, padding: '8px 18px', border: 'none',
                        background: view === v ? 'var(--color-ink)' : 'transparent',
                        color: view === v ? 'var(--color-btn-text)' : 'var(--color-ink)',
                      }}>
                {v === 'list' ? t('jobs.list') : t('jobs.map')}
              </button>
            ))}
          </div>
        </div>
      </div>

      {home && <p className="m-0 mb-4" style={{ fontSize: '1.15rem' }}>{t('jobs.tagline')}</p>}

      {home && ev && upcoming && (
        <Link to="/event" className="card p-4 mb-3 flex flex-wrap items-center gap-x-3 gap-y-1 no-underline"
              style={{ color: 'var(--color-ink)' }}>
          <span className="flex items-start gap-2">
            <CalendarDays size={22} aria-hidden="true" className="shrink-0 mt-0.5" />
            <span>
              <strong>{ev.name}</strong>
              {' · '}{t('jobs.event.line', { date: fmtDate(ev.date, lang), n: event?.employers.length ?? 0 })}
            </span>
          </span>
          <span className="font-medium underline ms-auto">{t('jobs.event.plan')}</span>
        </Link>
      )}

      <div className="card p-5 mb-3">
        <label htmlFor="ask-filters" className="font-medium block mb-1" style={{ fontSize: '1.15rem' }}>
          {t('jobs.lookingfor')}
        </label>
        <p id="ask-hint" className="m-0 mb-2 text-secondary">
          {t(window.SpeechRecognition ?? window.webkitSpeechRecognition ? 'jobs.lookingfor.hint' : 'jobs.lookingfor.hintwrite')}
        </p>
        <div className="flex gap-2 flex-wrap items-center">
          <input id="ask-filters" value={askText} maxLength={600}
                 aria-describedby="ask-hint"
                 placeholder={t('jobs.lookingfor.ex')}
                 onChange={(e) => setAskText(e.target.value)}
                 onKeyDown={(e) => { if (e.key === 'Enter') askFilters() }}
                 className="flex-1" style={{ minWidth: 220 }} />
          <VoiceInput compact targetId="ask-filters"
                      onText={(x) => setAskText((a) => (a ? `${a} ` : '') + x)} />
          <button type="button" className="btn btn-primary" disabled={askBusy}
                  onClick={askFilters}>
            {t('jobs.findjobs')}
          </button>
        </div>
        {askReply && (
          <div className="mt-3" role="status">
            <p className="m-0 font-medium">{t('jobs.weset')}</p>
            <ul className="m-0 mt-1 ps-5">
              {askReply.explanation.map((x, i) => <li key={i}>{x}</li>)}
            </ul>
            {askReply.not_understood.length > 0 && (
              <>
                <p className="m-0 mt-2 font-medium">{t('jobs.couldnot')}</p>
                <ul className="m-0 mt-1 ps-5 text-secondary">
                  {askReply.not_understood.map((x, i) => <li key={i}>{x}</li>)}
                </ul>
              </>
            )}
          </div>
        )}
      </div>

      {home && (
        <div className="card p-4 mb-3 flex flex-wrap items-center justify-between gap-3"
             style={{ background: 'var(--color-yes-bg)' }}>
          <p className="m-0 flex items-start gap-2">
            <LifeBuoy size={22} aria-hidden="true" className="shrink-0 mt-0.5" />
            <span><strong>{t('jobs.human.title')}</strong> {t('jobs.human.body')}</span>
          </p>
          <div className="flex flex-wrap gap-2">
            <Link to="/support" className="btn btn-secondary">{t('jobs.support.link')}</Link>
            <Link to="/help" className="btn btn-primary">{t('jobs.askadvisor')}</Link>
          </div>
        </div>
      )}

      {cat && !fitOpen && (
        <button type="button" className="btn btn-secondary w-full mb-3 justify-between"
                aria-expanded={false} onClick={() => setFitOpen(true)}>
          {t('jobs.fit.toggle')}
          <ChevronDown size={20} aria-hidden="true" />
        </button>
      )}

      {cat && fitOpen && (
        <div className="card p-5 mb-3 grid gap-5 md:grid-cols-2">
          <div>
            <label htmlFor="q-from" className="font-medium block mb-2" style={{ fontSize: '1.15rem' }}>
              {t('jobs.from')}
            </label>
            <select id="q-from" className="w-full" style={{ maxWidth: 360 }} value={params.get('district') ?? profileDistrict ?? ''}
                    onChange={(e) => set('district', e.target.value || null)}>
              <option value="">—</option>
              {cat.districts.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </select>
            {cfg.commute && (
              <div className="mt-3">
                <p id="q-commute" className="m-0 mb-2">{t('jobs.commute.filter')}</p>
                {originDistrict ? (
                  <div className="grid grid-cols-4 gap-2" role="group" aria-labelledby="q-commute">
                    {[15, 30, 45, 60].map((m) => (
                      <Toggle key={m} pressed={params.get('commute_max') === String(m)}
                              onClick={() => pickCommute(m)} className="justify-center">
                        {t('jobs.commute.tile', { m })}
                      </Toggle>
                    ))}
                  </div>
                ) : <p className="m-0 text-secondary">{t('jobs.commute.first')}</p>}
              </div>
            )}
          </div>
          <div>
            <h2 id="q-needs" className="m-0 mb-2 font-medium"
                style={{ fontSize: '1.15rem', fontFamily: 'inherit' }}>
              {t('jobs.myneeds')}
            </h2>
            <div className="flex flex-wrap gap-2" role="group" aria-labelledby="q-needs">
              {quickNeeds.map((k) => (
                <Toggle key={k} pressed={needKeys.includes(k)} onClick={() => toggleNeed(k)}>
                  {t(`cond.${k}` as Key)}
                </Toggle>
              ))}
            </div>
            {needKeys.length > 0 && (
              <fieldset className="mt-3 p-0 m-0 border-0">
                <legend className="sr-only">{t('jobs.needs')}</legend>
                {[['yes', t('jobs.needs.only')], ['not_no', t('jobs.needs.also')]].map(([v, label]) => (
                  <label key={v} className="flex items-center gap-2" style={{ minHeight: 44 }}>
                    <input type="radio" name="needs_mode_quick"
                           checked={(params.get('needs_mode') ?? 'yes') === v}
                           onChange={() => set('needs_mode', v)} />
                    {label}
                  </label>
                ))}
              </fieldset>
            )}
          </div>
        </div>
      )}

      <div className="overflow-x-auto mb-3 -mx-4 px-4"
           role="group" aria-label={t('jobs.filters')}>
        <div className="flex gap-2 w-max pe-4">
          <button type="button" className="btn btn-secondary whitespace-nowrap"
                  aria-expanded={more} onClick={() => setMore((m) => !m)}>
            <SlidersHorizontal size={20} aria-hidden="true" />
            {t('jobs.morefilters')}
          </button>
          {QUICK_LABELS.map((l) => (
            <Toggle key={l} pressed={params.getAll('label').includes(l)}
                    onClick={() => toggleLabel(l)}
                    className="whitespace-nowrap">
              {labelText(l, t)}
            </Toggle>
          ))}
          <Toggle pressed={!!params.get('near_station')}
                  onClick={() => set('near_station', params.get('near_station') ? null : '1')}
                  className="whitespace-nowrap">
            {t('jobs.nearstation')}
          </Toggle>
          <Toggle pressed={!!params.get('at_event')}
                  onClick={() => set('at_event', params.get('at_event') ? null : '1')}
                  className="whitespace-nowrap">
            {t('jobs.atevent')}
          </Toggle>
        </div>
      </div>

      {more && cat && (
        <div className="card p-5 mb-4" role="region" aria-label={t('jobs.filters')}>
          <div className="flex justify-between items-center mb-3 flex-wrap gap-2">
            <h2 className="m-0">{t('jobs.filters')}</h2>
            <div className="flex gap-2">
              {user?.role === 'resident' && (
                <button type="button" className="btn btn-quiet" onClick={useMyProfile}>
                  {t('jobs.useprofile')}
                </button>
              )}
              <button type="button" className="btn btn-quiet" onClick={clearAll}>
                {t('common.clearall')}
              </button>
            </div>
          </div>
          <h3 id="f-when">{t('jobs.whenwork')}</h3>
          <div className="grid gap-2 sm:grid-cols-3 mb-3" role="group" aria-labelledby="f-when">
            {TIME_GROUPS.map((g) => (
              <Toggle key={g.id} pressed={g.slots.every((x) => slotSet.has(x))}
                      onClick={() => toggleGroup(g.slots)} className="justify-center">
                {t(g.id)}
              </Toggle>
            ))}
          </div>
          <details className="mb-4">
            <summary className="cursor-pointer py-2">{t('jobs.time.days')}</summary>
          <div className="overflow-x-auto -mx-1 px-1 mt-2">
            <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(4, minmax(120px,1fr))' }}>
              <div />
              {PARTS.map((p) => <strong key={p}>{t(`part.${p}` as Key)}</strong>)}
              {DAYS.map((d) => (
                <div key={d} className="contents">
                  <strong className="self-center">{t(`dayfull.${d}` as Key)}</strong>
                  {PARTS.map((p) => {
                    const s = `${d}-${p}`
                    return (
                      <Toggle key={s} pressed={slotSet.has(s)}
                              onClick={() => toggleSlot(s)}
                              className="justify-center whitespace-nowrap">
                        {t(`part.${p}` as Key)}
                      </Toggle>
                    )
                  })}
                </div>
              ))}
            </div>
          </div>
          </details>
          <div className="grid gap-4 md:grid-cols-3">
            <Field label={t('jobs.maxhours')} id="f-hours">
              <input id="f-hours" type="number" min="1" inputMode="numeric"
                     value={params.get('hours_max') ?? ''}
                     onChange={(e) => set('hours_max', e.target.value || null)} />
            </Field>
            <Field label={t('jobs.minpay')} id="f-pay">
              <input id="f-pay" type="number" min="0" step="0.5" inputMode="decimal"
                     value={params.get('pay_min') ?? ''}
                     onChange={(e) => set('pay_min', e.target.value || null)} />
            </Field>
            <Field label={t('jobs.kind')} id="f-field">
              <select id="f-field" value={params.get('field') ?? ''}
                      onChange={(e) => set('field', e.target.value || null)}>
                <option value="">—</option>
                {cat.fields.map((f) => (
                  <option key={f.id} value={f.id}>{f.name}</option>
                ))}
              </select>
            </Field>
            <Field label={t('jobs.contract')} id="f-contract">
              <select id="f-contract" value={params.get('contract') ?? ''}
                      onChange={(e) => set('contract', e.target.value || null)}>
                <option value="">—</option>
                {cat.contract_types.map((c) => (
                  <option key={c} value={c}>{t(`contract.${c}` as Key)}</option>
                ))}
              </select>
            </Field>
            <Field label={t('jobs.experience')} id="f-exp">
              <select id="f-exp" value={params.get('experience') ?? ''}
                      onChange={(e) => set('experience', e.target.value || null)}>
                <option value="">—</option>
                {['none', 'some', 'required'].map((e) => (
                  <option key={e} value={e}>{t(`experience.${e}` as Key)}</option>
                ))}
              </select>
            </Field>
            <Field label={t('jobs.workmode')} id="f-mode">
              <select id="f-mode" value={params.get('work_mode') ?? ''}
                      onChange={(e) => set('work_mode', e.target.value || null)}>
                <option value="">—</option>
                <option value="on_site">{t('common.onsite')}</option>
                <option value="hybrid">{t('common.hybrid')}</option>
                <option value="remote">{t('common.remote')}</option>
              </select>
            </Field>
            <Field label={t('jobs.language')} id="f-lang">
              <select id="f-lang" value={params.get('language') ?? ''}
                      onChange={(e) => set('language', e.target.value || null)}>
                <option value="">—</option>
                <option>Finnish</option><option>English</option>
                <option>Swedish</option>
              </select>
            </Field>
            <Field label={t('jobs.mylevel')} id="f-level">
              <select id="f-level" value={params.get('level_max') ?? ''}
                      onChange={(e) => set('level_max', e.target.value || null)}>
                <option value="">—</option>
                {CEFR.map((l) => <option key={l} value={l}>{l}</option>)}
              </select>
            </Field>
            <Field label={`${t('jobs.distance')} (${t('jobs.km')})`} id="f-dist">
              <input id="f-dist" type="number" min="1" inputMode="numeric"
                     value={params.get('km') ?? ''} disabled={!params.get('district')}
                     onChange={(e) => set('km', e.target.value || null)} />
            </Field>
          </div>
          <h3 className="mt-5">{t('jobs.needs')}</h3>
          <div className="flex flex-wrap gap-2">
            {cat.condition_keys.map((c) => (
              <Toggle key={c.id} pressed={needKeys.includes(c.id)}
                      onClick={() => toggleNeed(c.id)}>
                {t(`cond.${c.id}` as Key)}
              </Toggle>
            ))}
          </div>
        </div>
      )}

      {activeFilterNames.length > 0 && (
        <div className="flex flex-wrap items-center gap-2 mb-4" role="group"
             aria-label={t('jobs.activefilters')}>
          <span className="text-secondary">{t('jobs.activefilters')}:</span>
          {activeFilterNames.map((f) => (
            <button key={f.key} type="button" className="chip wait" style={{ minHeight: 40 }}
                    onClick={() => removeFilter(f.key)}
                    aria-label={`${t('common.delete')} ${f.name}`}>
              <span className="dot" aria-hidden="true" />{f.name} ✕
            </button>
          ))}
          <button type="button" className="btn btn-quiet" style={{ minHeight: 40 }}
                  onClick={clearAll}>{t('common.clearall')}</button>
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[1fr_minmax(340px,42%)]">
        <section aria-label={t('jobs.list')}
                 className={view === 'map' ? 'hidden lg:block' : ''}>
          {jobs == null && params.get('commute_max') && (
            <p role="status">{t('jobs.commute.checking')}</p>
          )}
          {jobs == null && !params.get('commute_max') && (
            <p>{t('common.loading')}</p>
          )}
          {jobs?.length === 0 && (
            <div className="card p-6">
              <p className="font-medium">{t('jobs.empty')}</p>
              <EmptyHint params={params} />
              <Link to="/help" className="btn btn-primary mt-3">
                {t('jobs.askadvisor')}
              </Link>
            </div>
          )}
          {jobs?.map((j, i) => (
            <div key={j.id}>
              <JobRow job={j} selected={j.id === selected}
                      onShowOnMap={showOnMap}
                      saved={savedIds.has(j.id)}
                      onToggleSave={user?.role === 'resident' ? toggleSave : undefined}
                      actions={rowActions?.(j)}
                      originDistrict={originDistrict}
                      originName={originName}
                      needs={needKeys}
                      districtName={cat ? districtName(j.district, cat.districts) : j.district} />
              {i === 2 && !home && <HelpCard />}
            </div>
          ))}
          {jobs && jobs.length > 3 && <HelpCard />}
        </section>
        <aside id="map-panel" aria-label={t('jobs.map')}
               className={`${view === 'map' ? '' : 'hidden lg:block'} lg:sticky lg:top-4 self-start w-full`}>
          <a href="#main" className="skip-link">{t('jobs.skipmap')}</a>
          <div className="card overflow-hidden">
            <JobMap jobs={jobs ?? []} selectedId={selected}
                    onSelect={onSelectMarker} height={520} />
          </div>
          {selectedJob && (
            <div className="card p-4 mt-3">
              <h3 className="m-0 font-display" style={{ fontSize: '1.15rem' }}>
                {selectedJob.title}
              </h3>
              <p className="m-0 text-secondary">{selectedJob.employer?.name}</p>
              <Link to={`/jobs/${selectedJob.id}`} className="btn btn-primary mt-3">
                {t('jobs.opendetails')}
              </Link>
            </div>
          )}
        </aside>
      </div>
    </div>
  )
}

function EmptyHint({ params }: { params: URLSearchParams }) {
  const { t } = useI18n()
  const [best, setBest] = useState<string | null>(null)
  useEffect(() => {
    let cancelled = false
    const candidates = ['slots', 'needs', 'field', 'district', 'language']
      .filter((k) => params.get(k))
    Promise.all(candidates.map(async (k) => {
      const p = new URLSearchParams(params)
      p.delete(k)
      const r = await api<{ count: number }>(`/api/jobs?${p.toString()}`)
      return { k, count: r.count }
    })).then((rs) => {
      if (cancelled || !rs.length) return
      rs.sort((a, b) => b.count - a.count)
      setBest(rs[0].k)
    }).catch(() => {})
    return () => { cancelled = true }
  }, [params])
  if (!best) return null
  const names: Record<string, string> = {
    slots: t('jobs.whenwork'), needs: t('jobs.needs'), field: t('jobs.kind'),
    district: t('jobs.distance'), language: t('jobs.language'),
  }
  return <p className="text-secondary mt-2">{t('jobs.emptyhint')} {names[best]}</p>
}
