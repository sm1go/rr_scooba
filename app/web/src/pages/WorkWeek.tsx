import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Bundle, Catalog } from '../types'
import { ErrorBox, Field, Toggle } from '../components/ui'
import { districtName, hoursLine } from '../lib/format'

const HOURS = [12, 18, 25, 30, 37]
const KMS = [3, 5, 10]
const DAY_KEYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
const LETTERS = ['A', 'B', 'C']
const JOB_COLORS = ['var(--color-yes)', '#b45309', '#6d28d9']
const SLOT_PRESETS = [
  { id: 'mornings', slots: ['mon-morning', 'tue-morning', 'wed-morning', 'thu-morning', 'fri-morning'] },
  { id: 'daytime', slots: ['mon-morning', 'mon-afternoon', 'tue-morning', 'tue-afternoon', 'wed-morning', 'wed-afternoon', 'thu-morning', 'thu-afternoon', 'fri-morning', 'fri-afternoon'] },
  { id: 'evenings', slots: ['mon-evening', 'tue-evening', 'wed-evening', 'thu-evening', 'fri-evening', 'sat-morning', 'sat-afternoon', 'sat-evening', 'sun-morning', 'sun-afternoon', 'sun-evening'] },
]

export default function WorkWeek() {
  const { t } = useI18n()
  const { user } = useAuth()
  const [params, setParams] = useSearchParams()
  const [cat, setCat] = useState<Catalog | null>(null)
  const [data, setData] = useState<{ target: number; candidates: number; bundles: Bundle[] } | null>(null)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)

  const set = (k: string, v: string | null) => {
    const p = new URLSearchParams(params)
    if (v == null || v === '') p.delete(k); else p.set(k, v)
    setParams(p)
  }
  const hours = +(params.get('hours') ?? '30')
  const slotSet = new Set((params.get('slots') ?? '').split(',').filter(Boolean))
  const toggleSlots = (preset: string[]) => {
    const s = new Set(slotSet)
    const on = preset.every((x) => s.has(x))
    preset.forEach((x) => { if (on) s.delete(x); else s.add(x) })
    set('slots', [...s].join(',') || null)
  }

  useEffect(() => { api<Catalog>('/api/catalog').then(setCat).catch(() => undefined) }, [])
  useEffect(() => {
    setBusy(true); setErr('')
    const q = new URLSearchParams(params)
    api<typeof data>(`/api/bundles?${q}`)
      .then((r) => setData(r))
      .catch(() => { setErr(t('common.error')); setData(null) })
      .finally(() => setBusy(false))
  }, [params, t])

  const saveAll = async (b: Bundle) => {
    await Promise.all(b.jobs.map((j) =>
      api(`/api/me/saved/${j.id}`, { method: 'PUT' }).catch(() => undefined)))
    alert(t('week.saved'))
  }

  return (
    <div className="max-w-5xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('week.title')}</h1>
      <p className="text-secondary">{t('week.intro')}</p>

      <div className="card p-5 mb-4 grid gap-4 md:grid-cols-2">
        <div>
          <p className="font-medium m-0 mb-2">{t('week.target')}</p>
          <div className="flex flex-wrap gap-2">
            {HOURS.map((h) => (
              <Toggle key={h} pressed={hours === h}
                      onClick={() => set('hours', String(h))}>
                {h} {t('common.hweek')}
              </Toggle>
            ))}
          </div>
        </div>
        <div>
          <p className="font-medium m-0 mb-2">{t('jobs.whenwork')}</p>
          <div className="flex flex-wrap gap-2">
            {SLOT_PRESETS.map((p) => (
              <Toggle key={p.id}
                      pressed={p.slots.every((x) => slotSet.has(x)) && slotSet.size > 0}
                      onClick={() => toggleSlots(p.slots)}>
                {t(`week.slots.${p.id}` as Key)}
              </Toggle>
            ))}
          </div>
        </div>
        <div>
          <Field label={t('week.fromwhere')} id="ww-dist">
            <select id="ww-dist" value={params.get('district') ?? ''}
                    onChange={(e) => set('district', e.target.value || null)}>
              <option value="">{t('common.anywhere')}</option>
              {cat?.districts.map((d) => (
                <option key={d.id} value={d.id}>{d.name}</option>
              ))}
            </select>
          </Field>
          <div className="flex flex-wrap gap-2 mt-2">
            {KMS.map((k) => (
              <Toggle key={k} pressed={params.get('km') === String(k)}
                      disabled={!params.get('district')}
                      onClick={() => set('km', params.get('km') === String(k) ? null : String(k))}>
                {k} km
              </Toggle>
            ))}
          </div>
        </div>
        <Field label={t('week.word')} id="ww-q">
          <input id="ww-q" value={params.get('q') ?? ''}
                 onChange={(e) => set('q', e.target.value || null)}
                 placeholder={t('week.wordhint')} />
        </Field>
      </div>
      <p className="text-secondary">{t('week.gap')}</p>

      {err && <ErrorBox>{err}</ErrorBox>}
      {busy && <p role="status">{t('common.loading')}</p>}
      {data && !busy && (
        <>
          <p className="font-medium" role="status">
            {t('week.count', { n: data.bundles.length })}
          </p>
          {data.bundles.length === 0 && (
            <div className="card p-5" role="status">
              <p className="m-0">
                {data.candidates === 0 ? t('week.none0') : t('week.none1')}
              </p>
            </div>
          )}
          {data.bundles.map((b, i) => (
            <BundleCard key={i} b={b} cat={cat} t={t}
                        isResident={user?.role === 'resident' || !user}
                        signedIn={!!user} onSave={() => saveAll(b)} />
          ))}
        </>
      )}
    </div>
  )
}

function BundleCard({ b, cat, t, isResident, signedIn, onSave }: {
  b: Bundle; cat: Catalog | null
  t: ReturnType<typeof useI18n>['t']
  isResident: boolean; signedIn: boolean; onSave: () => void
}) {
  const letters = useMemo(
    () => new Map(b.jobs.map((j, i) => [j.id, LETTERS[i]])), [b])
  return (
    <article className="card p-5 mb-4">
      <h2 className="m-0 font-display" style={{ fontSize: '1.15rem' }}>
        {t('week.head', { h: b.hours_min === b.hours_max ? String(b.hours_max) : `${b.hours_min}–${b.hours_max}`, n: b.jobs.length })}
        {` · ${t('week.kmapart', { km: b.max_km_apart })}`}
        {b.pay_week_eur != null &&
          ` · ${t('week.pay', { eur: b.pay_week_eur.toFixed(0) })}`}
      </h2>

      <div className="week-grid grid grid-cols-7 gap-1 mt-3" role="table"
           aria-label={t('week.grid')}>
        {DAY_KEYS.map((d) => (
          <div key={d} role="columnheader"
               className="text-center text-secondary">{t(`dayfull.${d}` as Key).slice(0, 3)}</div>
        ))}
        {DAY_KEYS.map((d) => (
          <div key={d} role="cell" className="min-h-[60px] border rounded p-1"
               style={{ borderColor: 'var(--color-hairline)' }}>
            {(b.week[d] ?? []).map((s, i) => {
              const idx = b.jobs.findIndex((j) => j.id === s.job_id)
              return (
                <div key={i} className="rounded px-1 mb-1 font-medium"
                     style={{
                       background: JOB_COLORS[idx], color: '#fff',
                       fontSize: '1rem', lineHeight: 1.3,
                     }}>
                  {letters.get(s.job_id)} {s.start}–{s.end}
                </div>
              )
            })}
          </div>
        ))}
      </div>

      <ul className="m-0 mt-4 p-0 list-none grid gap-2">
        {b.jobs.map((j, i) => (
          <li key={j.id} className="flex flex-wrap items-baseline gap-x-2">
            <span className="rounded px-2 font-medium shrink-0"
                  style={{ background: JOB_COLORS[i], color: '#fff' }}
                  aria-hidden="true">{LETTERS[i]}</span>
            <Link to={`/jobs/${j.id}`} className="font-medium">{j.title}</Link>
            <span className="text-secondary">
              {j.employer?.name}
              {cat ? ` · ${districtName(j.district, cat.districts)}` : ''}
              {hoursLine(j, t) ? ` · ${hoursLine(j, t)}` : ''}
            </span>
            <Link to={`/jobs/${j.id}/apply`} className="text-secondary">
              {t('common.apply')}
            </Link>
          </li>
        ))}
      </ul>

      <div className="flex flex-wrap gap-2 mt-4">
        {signedIn && isResident && (
          <button type="button" className="btn btn-secondary" onClick={onSave}>
            {t('week.saveall')}
          </button>
        )}
        <Link className="btn btn-primary"
              to={`/help?kind=prepare_application&jobs=${b.jobs.map((j) => j.id).join(',')}`}>
          {t('week.advisorhelp')}
        </Link>
      </div>
      <p className="m-0 mt-2 text-secondary">{t('week.limit')}</p>
    </article>
  )
}
