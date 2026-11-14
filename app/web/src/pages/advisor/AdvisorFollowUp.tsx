import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { Overview } from '../../types'
import { Chip, ErrorBox, ErrorState, Section, Toggle } from '../../components/ui'
import { fmtDate } from '../../lib/format'
import { staffHas, useStaffT, type StaffKey } from '../../i18n-staff'

type CallOutcome = 'still_open' | 'filled' | 'no_answer' | 'no_vacancy'
interface Outcomes {
  help_requests: { new: number; in_progress: number; done: number }
  applications: number
  applications_by_advisor: number
  interviews: number
  offers: number
  event_talks: { recorded: number; answered: number; unanswered: number }
  employer_calls: Record<CallOutcome, number>
}
type StaffOverview = Omit<Overview, 'event_talks_unanswered'> & {
  outcomes: { last_7_days: Outcomes; all_time: Outcomes }
  event_talks_unanswered: (Overview['event_talks_unanswered'][number] & { recorded_by_advisor?: boolean })[]
}
interface CallEmployer {
  id: string; name: string; contact_name: string; contact_email: string; contact_phone: string
  reason: 'call_again' | 'no_open_job' | 'stale'; open_jobs: number
  newest_confirmed_days_ago: number | null; latest_job_id: string | null
  last_call: { outcome: CallOutcome; at: string } | null
}
interface BoothStats {
  employer_id: string; name: string; booth: string; visitors_planned: number
  talks: number; answered: number; next_step: number; answered_pct: number | null
}
interface EventOverview {
  event: { id: string; name: string; date: string } | null
  employers: BoothStats[]
  totals: Omit<BoothStats, 'employer_id' | 'name' | 'booth'> | null
}
interface AuditEvent { id: number; action: string; detail: string; created_at: string }

const ROW = { borderColor: 'var(--color-hairline)' }
const tel = (p: string) => `tel:${p.replace(/[^\d+]/g, '')}`

function Stat({ value, label, sub }: { value: number | string; label: string; sub?: string }) {
  return (
    <div className="card p-4 text-center">
      <div className="font-display" style={{ fontSize: '2rem' }}>{value}</div>
      <div className="font-medium">{label}</div>
      {sub && <div className="text-secondary" style={{ fontSize: '0.95rem' }}>{sub}</div>}
    </div>
  )
}

function Counts({ title, items }: { title: string; items: [string, number][] }) {
  return (
    <div className="card p-4">
      <p className="m-0 font-medium">{title}</p>
      <ul className="m-0 mt-1 p-0 list-none">
        {items.map(([l, n]) => (
          <li key={l} className="flex justify-between gap-2"><span>{l}</span><strong>{n}</strong></li>
        ))}
      </ul>
    </div>
  )
}

export default function AdvisorFollowUp() {
  const { t, lang } = useI18n()
  const s = useStaffT()
  const [ov, setOv] = useState<StaffOverview | null>(null)
  const [events, setEvents] = useState<AuditEvent[]>([])
  const [toCall, setToCall] = useState<CallEmployer[]>([])
  const [evo, setEvo] = useState<EventOverview | null>(null)
  const [week, setWeek] = useState(true)
  const [err, setErr] = useState<unknown>(null)
  const [callErr, setCallErr] = useState('')

  const load = () => {
    setErr(null)
    api<StaffOverview>('/api/advisor/overview').then(setOv).catch((e) => setErr(e))
    api<{ events: AuditEvent[] }>('/api/audit?limit=50').then((r) => setEvents(r.events)).catch(() => {})
    api<{ employers: CallEmployer[] }>('/api/advisor/employers-to-call')
      .then((r) => setToCall(r.employers)).catch(() => {})
    api<EventOverview>('/api/advisor/event-overview').then(setEvo).catch(() => {})
  }
  useEffect(load, [])

  const logCall = async (employer_id: string, outcome: CallOutcome) => {
    setCallErr('')
    try {
      await api('/api/advisor/calls', { body: { employer_id, outcome } })
      load()
    } catch (e) { setCallErr(e instanceof ApiError ? e.message : t('common.error')) }
  }

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!ov) return <p>{t('common.loading')}</p>
  const o = week ? ov.outcomes.last_7_days : ov.outcomes.all_time
  const hr = o.help_requests
  const actionLabel = (a: string) => s(staffHas(`act.${a}`) ? `act.${a}` as StaffKey : 'act.other')

  return (
    <div className="max-w-4xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('advisor.followup')}</h1>

      <Section title={s('out.title')} action={
        <div className="flex gap-2 flex-wrap">
          <Toggle pressed={week} onClick={() => setWeek(true)}>{s('out.week')}</Toggle>
          <Toggle pressed={!week} onClick={() => setWeek(false)}>{s('out.all')}</Toggle>
        </div>
      }>
        <ol className="grid gap-3 md:grid-cols-4 m-0 p-0 list-none" aria-label={s('out.title')}>
          <li><Stat value={hr.new + hr.in_progress + hr.done + o.event_talks.recorded}
                    label={`${s('out.contacts')} →`} sub={s('out.contacts.sub')} /></li>
          <li><Stat value={o.applications} label={`${s('out.applications')} →`}
                    sub={s('out.applications.sub', { n: o.applications_by_advisor })} /></li>
          <li><Stat value={o.interviews} label={`${s('out.interviews')} →`} sub={s('out.interviews.sub')} /></li>
          <li><Stat value={o.offers} label={s('out.offers')} /></li>
        </ol>
        <div className="grid gap-3 md:grid-cols-3 mt-3">
          <Counts title={s('out.help')} items={[
            [s('out.help.new'), hr.new], [s('out.help.in_progress'), hr.in_progress],
            [s('out.help.done'), hr.done]]} />
          <Counts title={s('out.talks')} items={[
            [s('out.talks.recorded'), o.event_talks.recorded],
            [s('out.talks.answered'), o.event_talks.answered],
            [s('out.talks.unanswered'), o.event_talks.unanswered]]} />
          <Counts title={s('out.calls')} items={(Object.keys(o.employer_calls) as CallOutcome[])
            .map((k) => [s(`call.${k}`), o.employer_calls[k]])} />
        </div>
        <p className="m-0 mt-3 text-secondary">{s('out.note')}</p>
      </Section>

      <div className="grid gap-3 md:grid-cols-3 mb-5">
        <Stat value={ov.open_jobs} label={t('advisor.openjobs')} />
        <Stat value={ov.stale_jobs.length} label={t('advisor.stalejobs')} />
        <Stat value={ov.new_help_requests} label={t('advisor.requests')} />
      </div>

      <Section title={s('emp.title')}>
        <p className="mt-0 text-secondary">{s('emp.intro')}</p>
        {callErr && <ErrorBox>{callErr}</ErrorBox>}
        {toCall.length === 0 && <p className="text-secondary">{s('emp.none')}</p>}
        {toCall.map((e) => (
          <div key={e.id} className="py-3 border-b flex justify-between gap-3 flex-wrap" style={ROW}>
            <div className="min-w-0">
              <strong>{e.name}</strong>
              <p className="m-0">
                {e.contact_name}
                {e.contact_phone && <> · <a href={tel(e.contact_phone)}>{e.contact_phone}</a></>}
                {e.contact_email && <> · <a href={`mailto:${e.contact_email}`}>{e.contact_email}</a></>}
              </p>
              <p className="m-0 text-secondary" style={{ fontSize: '1rem' }}>
                {e.last_call
                  ? s('emp.lastcall', { o: s(`call.${e.last_call.outcome}`), d: fmtDate(e.last_call.at, lang) })
                  : s('emp.nevercalled')}
              </p>
            </div>
            <div className="flex flex-col gap-2 items-end">
              <Chip tone={e.reason === 'call_again' ? 'no' : 'wait'}>
                {s(`emp.reason.${e.reason}`, { n: e.newest_confirmed_days_ago ?? '' })}
              </Chip>
              <div className="flex gap-2 flex-wrap justify-end">
                {e.latest_job_id ? (
                  <Link className="btn btn-secondary" to={`/advisor/jobs/${e.latest_job_id}/call`}>
                    {s('emp.prepare')}
                  </Link>
                ) : (
                  <>
                    <button type="button" className="btn btn-quiet" onClick={() => logCall(e.id, 'no_answer')}>
                      {s('cs.no_answer')}
                    </button>
                    <button type="button" className="btn btn-quiet" onClick={() => logCall(e.id, 'no_vacancy')}>
                      {s('call.no_vacancy')}
                    </button>
                    <Link className="btn btn-secondary" to={`/advisor/jobs/new?employer=${e.id}`}>
                      {s('emp.addjob')}
                    </Link>
                  </>
                )}
              </div>
            </div>
          </div>
        ))}
      </Section>

      <Section title={t('advisor.stalejobs')}>
        {ov.stale_jobs.length === 0 && <p className="text-secondary">{t('advisor.empty')}</p>}
        {ov.stale_jobs.map((j) => (
          <div key={j.id} className="flex justify-between gap-3 py-2 border-b" style={ROW}>
            <div>
              <Link to={`/jobs/${j.id}`}>{j.title}</Link>
              <span className="text-secondary"> — {j.employer_name}</span>
              {' · '}<Link to={`/advisor/jobs/${j.id}/call`}>{s('emp.prepare')}</Link>
            </div>
            <Chip tone="wait">{j.confirmed_days_ago} {t('common.days')}</Chip>
          </div>
        ))}
      </Section>

      <Section title={t('advisor.waiting')}>
        {ov.waiting_over_7_days.length === 0 && <p className="text-secondary">{t('advisor.empty')}</p>}
        {ov.waiting_over_7_days.map((a) => (
          <div key={a.id} className="py-2 border-b" style={ROW}>
            <Link to={`/jobs/${a.job_id}`}>{a.job_title}</Link>
            <span className="text-secondary">
              {' — '}{a.applicant_name} · {t(`status.${a.status}` as Key)}
              {' · '}{a.days_waiting} {t('common.days')}
            </span>
            {a.employer && (
              <p className="m-0 text-secondary" style={{ fontSize: '1rem' }}>
                {a.employer.name} · {a.employer.contact_email} · {a.employer.contact_phone}
              </p>
            )}
          </div>
        ))}
      </Section>

      {evo?.event && evo.totals && (
        <Section title={`${s('ev.title')} — ${evo.event.name}`}
                 action={<Link className="btn btn-secondary" to="/event">{s('wu.button')}</Link>}>
          <div style={{ overflowX: 'auto' }}>
            <table className="w-full" style={{ borderCollapse: 'collapse' }}>
              <thead>
                <tr className="text-left">
                  {(['ev.booth', 'ev.employer', 'ev.planned', 'ev.talks', 'ev.answered', 'ev.next'] as const)
                    .map((k) => <th key={k} scope="col" className="py-1 pr-3">{s(k)}</th>)}
                </tr>
              </thead>
              <tbody>
                {evo.employers.map((b) => (
                  <tr key={b.employer_id} className="border-b" style={ROW}>
                    <td className="py-1 pr-3">{b.booth}</td>
                    <td className="py-1 pr-3">{b.name}</td>
                    <td className="py-1 pr-3">{b.visitors_planned}</td>
                    <td className="py-1 pr-3">{b.talks}</td>
                    <td className="py-1 pr-3">{b.answered_pct === null ? '—' : `${b.answered_pct} %`}</td>
                    <td className="py-1 pr-3">{b.next_step}</td>
                  </tr>
                ))}
                <tr className="font-medium">
                  <td className="py-1 pr-3" colSpan={2}>{s('ev.total')}</td>
                  <td className="py-1 pr-3">{evo.totals.visitors_planned}</td>
                  <td className="py-1 pr-3">{evo.totals.talks}</td>
                  <td className="py-1 pr-3">{evo.totals.answered_pct === null ? '—' : `${evo.totals.answered_pct} %`}</td>
                  <td className="py-1 pr-3">{evo.totals.next_step}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </Section>
      )}

      {ov.event_talks_unanswered.length > 0 && (
        <Section title={t('advisor.followup.talks')}>
          {ov.event_talks_unanswered.map((tk) => (
            <div key={tk.id} className="py-2 border-b" style={ROW}>
              <strong>{tk.person_name}</strong>
              <span className="text-secondary">
                {' — '}{tk.employer_name} · {tk.days_waiting} {t('common.days')}
              </span>
              {tk.recorded_by_advisor && (
                <p className="m-0 text-secondary" style={{ fontSize: '1rem' }}>{s('wu.byadvisor')}</p>
              )}
              {tk.employer && (
                <p className="m-0 text-secondary" style={{ fontSize: '1rem' }}>
                  {tk.employer.contact_name}
                  {tk.employer.contact_phone && <> · <a href={tel(tk.employer.contact_phone)}>{tk.employer.contact_phone}</a></>}
                  {tk.employer.contact_email && <> · <a href={`mailto:${tk.employer.contact_email}`}>{tk.employer.contact_email}</a></>}
                </p>
              )}
            </div>
          ))}
        </Section>
      )}

      <details className="card p-5 mb-5">
        <summary className="font-medium" style={{ cursor: 'pointer' }}>
          {t('advisor.activity')} — {s('act.show', { n: events.length })}
        </summary>
        <ul className="m-0 mt-3 p-0 list-none">
          {events.map((e) => (
            <li key={e.id} className="py-1 border-b" style={{ ...ROW, fontSize: '1rem' }}>
              <span className="text-secondary">{fmtDate(e.created_at, lang)}</span>
              {' — '}{actionLabel(e.action)}
              {e.action === 'call_logged' && (() => {
                const oc = e.detail.split(':')[2]
                return staffHas(`call.${oc}`) ? `: ${s(`call.${oc}` as StaffKey)}` : ''
              })()}
            </li>
          ))}
        </ul>
      </details>
    </div>
  )
}
