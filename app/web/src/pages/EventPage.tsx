import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { EventInfo, EventPlan } from '../types'
import { ErrorBox, ErrorState, Field, Section } from '../components/ui'
import { useStaffT } from '../i18n-staff'
import BoothPlan from '../components/BoothPlan'

const EMPTY_TALK = { employer_id: '', first_name: '', contact_method: 'phone', contact_value: '', job_id: '', consent: false }

/** Advisor: record a talk for a walk-up visitor with no account or number. */
function RecordTalk({ info }: { info: EventInfo }) {
  const { t } = useI18n()
  const s = useStaffT()
  const [open, setOpen] = useState(false)
  const [f, setF] = useState(EMPTY_TALK)
  const [err, setErr] = useState('')
  const [saved, setSaved] = useState(false)
  const emp = info.employers.find((e) => e.id === f.employer_id)
  const ready = f.employer_id && f.first_name.trim() && f.contact_value.trim().length >= 3 && f.consent

  const save = async () => {
    setErr('')
    try {
      await api('/api/advisor/event/talks', { body: { ...f, job_id: f.job_id || null } })
      setSaved(true); setOpen(false); setF(EMPTY_TALK)
    } catch (e) { setErr(e instanceof ApiError ? e.message : t('common.error')) }
  }

  if (!open) {
    return (
      <div className="mb-5">
        {saved && <p className="card p-4 font-medium" role="status">{s('wu.saved')}</p>}
        <button type="button" className="btn btn-primary"
                onClick={() => { setOpen(true); setSaved(false) }}>
          {s('wu.button')}
        </button>
      </div>
    )
  }
  return (
    <Section title={s('wu.button')}>
      <p className="mt-0 text-secondary">{s('wu.intro')}</p>
      {err && <ErrorBox>{err}</ErrorBox>}
      <Field label={s('wu.employer')} id="wu-emp">
        <select id="wu-emp" value={f.employer_id}
                onChange={(e) => setF({ ...f, employer_id: e.target.value, job_id: '' })}>
          <option value="">{s('wu.choose')}</option>
          {info.employers.map((e) => <option key={e.id} value={e.id}>{e.booth} — {e.name}</option>)}
        </select>
      </Field>
      <Field label={s('wu.name')} id="wu-name">
        <input id="wu-name" value={f.first_name} maxLength={60} autoComplete="off"
               onChange={(e) => setF({ ...f, first_name: e.target.value })} />
      </Field>
      <Field label={s('wu.method')} id="wu-method">
        <select id="wu-method" value={f.contact_method}
                onChange={(e) => setF({ ...f, contact_method: e.target.value })}>
          {(['phone', 'sms', 'email'] as const).map((m) => <option key={m} value={m}>{s(`wu.${m}`)}</option>)}
        </select>
      </Field>
      <Field label={s('wu.value')} id="wu-value">
        <input id="wu-value" value={f.contact_value} autoComplete="off"
               type={f.contact_method === 'email' ? 'email' : 'tel'}
               onChange={(e) => setF({ ...f, contact_value: e.target.value })} />
      </Field>
      {emp && emp.jobs.length > 0 && (
        <Field label={s('wu.job')} id="wu-job">
          <select id="wu-job" value={f.job_id} onChange={(e) => setF({ ...f, job_id: e.target.value })}>
            <option value="">{s('wu.nojob')}</option>
            {emp.jobs.map((j) => <option key={j.id} value={j.id}>{j.title}</option>)}
          </select>
        </Field>
      )}
      <label className="flex gap-2 items-start mb-3">
        <input type="checkbox" checked={f.consent} style={{ width: 24, height: 24 }}
               onChange={(e) => setF({ ...f, consent: e.target.checked })} />
        <span>{s('wu.consent')}</span>
      </label>
      <div className="flex gap-2 flex-wrap">
        <button type="button" className="btn btn-quiet" onClick={() => setOpen(false)}>{s('wu.cancel')}</button>
        <button type="button" className="btn btn-primary" disabled={!ready} onClick={save}>{s('wu.save')}</button>
      </div>
    </Section>
  )
}

/** /event — the recruitment event: booth plan, employer list, My plan. */
export default function EventPage() {
  const { t } = useI18n()
  const { user } = useAuth()
  const [info, setInfo] = useState<EventInfo | null>(null)
  const [plan, setPlan] = useState<EventPlan | null>(null)
  const [err, setErr] = useState<unknown>(null)

  const load = () => {
    setErr(null)
    api<EventInfo>('/api/event').then(setInfo).catch(setErr)
    if (user?.role === 'resident') {
      api<EventPlan>('/api/me/event-plan').then(setPlan).catch(() => setPlan(null))
    } else setPlan(null)
  }
  useEffect(load, [user])

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!info) return <p>{t('common.loading')}</p>
  if (!info.event) {
    return (
      <div className="max-w-3xl mx-auto">
        <h1 data-page-title tabIndex={-1}>{t('event.title')}</h1>
        <p className="card p-5">{t('event.empty')}</p>
      </div>
    )
  }
  const ev = info.event
  const inPlan = new Set(plan?.booths.map((b) => b.employer_id) ?? [])

  const setPlanItem = async (employerId: string, add: boolean) => {
    try {
      const r = await api<EventPlan>(`/api/me/event-plan/${employerId}`,
        { method: add ? 'PUT' : 'DELETE' })
      setPlan(r)
    } catch { /* sign-in guard handles */ }
  }

  return (
    <div className="grid gap-4">
      <p className="card p-4 font-medium">{ev.advisor_note || t('event.advisor')}</p>
      {user?.role === 'advisor' && <RecordTalk info={info} />}

      {user?.role === 'resident' && plan?.code && (
        <Section title={t('event.myplan')}>
          <div className="card p-5 mb-3 text-center">
            <p className="m-0 text-secondary">{t('event.number')}</p>
            <p className="m-0 font-display" style={{ fontSize: '4rem', lineHeight: 1.1 }}
               aria-label={`${t('event.number')} ${plan.code.split('').join(' ')}`}>
              {plan.code}
            </p>
            <p className="m-0 mt-2 text-secondary">{t('event.numberwhy')}</p>
          </div>
          {plan.booths.length === 0 && (
            <p className="text-secondary">{t('event.planempty')}</p>
          )}
          <ol className="m-0 p-0 list-none">
            {plan.booths.map((b) => (
              <li key={b.employer_id} className="card p-4 mb-2 flex justify-between gap-3 flex-wrap">
                <div>
                  <strong>{b.booth}</strong> — {b.name}
                  <ul className="m-0 mt-1 pl-5 text-secondary">
                    {b.jobs.map((j) => (
                      <li key={j.id}><Link to={`/jobs/${j.id}`}>{j.title}</Link></li>
                    ))}
                  </ul>
                </div>
                <button type="button" className="btn btn-quiet"
                        onClick={() => setPlanItem(b.employer_id, false)}>
                  {t('event.remove')}
                </button>
              </li>
            ))}
          </ol>
          {plan.booths.length > 0 && (
            <Link to="/event/print" className="btn btn-primary mt-2">
              {t('event.print')}
            </Link>
          )}
        </Section>
      )}
      {!user && (
        <p className="card p-4">
          <Link to={`/sign-in?back=${encodeURIComponent('/event')}`}>{t('event.signin')}</Link>
        </p>
      )}

      <BoothPlan employers={info.employers} inPlan={inPlan} />

      <Section title={t('event.openjobs')}>
        {info.employers.map((e) => (
          <div key={e.id} className="card p-4 mb-3">
            <div className="flex justify-between gap-3 flex-wrap">
              <div>
                <strong>{e.booth}</strong> —{' '}
                <Link to={`/companies/${e.id}`}>{e.name}</Link>
              </div>
              {user?.role === 'resident' && (
                inPlan.has(e.id) ? (
                  <button type="button" className="btn btn-quiet"
                          onClick={() => setPlanItem(e.id, false)}>
                    {t('event.inplan')} ✓
                  </button>
                ) : (
                  <button type="button" className="btn btn-secondary"
                          onClick={() => setPlanItem(e.id, true)}>
                    {t('event.addplan')}
                  </button>
                )
              )}
            </div>
            <ul className="m-0 mt-2 pl-5">
              {e.jobs.map((j) => (
                <li key={j.id}><Link to={`/jobs/${j.id}`}>{j.title}</Link></li>
              ))}
            </ul>
          </div>
        ))}
      </Section>
    </div>
  )
}
