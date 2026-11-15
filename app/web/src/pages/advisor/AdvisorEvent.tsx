import { useEffect, useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useConfig } from '../../lib/config'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { AdvisorBoard, OrganizerDay, OrganizerReport } from '../../types'
import { ErrorState, Section } from '../../components/ui'
import { Tabs } from '../../components/Tabs'
import { EMPTY_NEED, NeedCardForm } from '../employer/EmployerEventWorkspace'
import type { NeedCardDraft } from '../employer/EmployerEventWorkspace'

function fmtTime(iso: string) {
  return iso.includes('T') ? iso.split('T')[1].slice(0, 5) : iso
}

function fmtDate(iso: string) {
  try {
    return new Date(iso.length === 10 ? iso + 'T00:00:00' : iso)
      .toLocaleDateString(document.documentElement.lang || 'en',
        { day: 'numeric', month: 'long', year: 'numeric' })
  } catch { return iso }
}

/** Demo/real clock: fetch /api/demo/state once (no ticking needed). */
function useNow() {
  const cfg = useConfig()
  const [offset, setOffset] = useState(0)
  useEffect(() => {
    if (!cfg.demo) return
    api<{ now: string }>('/api/demo/state')
      .then((d) => setOffset(Date.parse(d.now) - Date.now()))
      .catch(() => {})
  }, [cfg.demo])
  return new Date(Date.now() + offset)
}

function daysUntil(iso: string, now: Date) {
  const ms = new Date(iso + 'T00:00:00').getTime() - now.getTime()
  return Math.max(0, Math.ceil(ms / 86400000))
}

const NEED_STYLE: Record<string, { bg: string; fg: string }> = {
  on_time: { bg: 'var(--color-yes-bg)', fg: 'var(--color-ink)' },
  late: { bg: '#fef3c7', fg: 'var(--color-ink)' },
  missing: { bg: 'var(--color-no-bg)', fg: 'var(--color-ink)' },
}

function LiveBoard({ id }: { id: string }) {
  const { t } = useI18n()
  const [day, setDay] = useState<OrganizerDay | null>(null)
  const load = () => api<OrganizerDay>(`/api/advisor/events/${id}/day`)
    .then(setDay).catch(() => setDay(null))
  useEffect(() => { load() }, [id]) // eslint-disable-line react-hooks/exhaustive-deps
  if (!day) return <p>{t('common.loading')}</p>
  const offer = async (employerId: string) => {
    try {
      await api(`/api/advisor/events/${id}/offer`,
                { body: { employer_id: employerId } })
      load()
    } catch (e) { alert(e instanceof ApiError ? e.message : t('common.error')) }
  }
  return (
    <div className="overflow-x-auto">
      <table className="w-full" style={{ borderCollapse: 'collapse' }}>
        <thead>
          <tr>
            {[t('ev.org.e'), t('ev.org.day.now'), t('ev.org.day.done'),
              t('ev.org.day.noshow'), t('ev.org.day.free'),
              t('ev.org.day.queue'), ''].map((h, i) => (
              <th key={i} className="text-start p-2"
                  style={{ borderBottom: '2px solid var(--color-hairline)' }}>
                {h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {day.booths.map((b) => (
            <tr key={b.employer_id}>
              <td className="p-2"
                  style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                <strong>{b.name}</strong>
                {b.booth && <span className="block text-secondary">
                  {t('ev.booth')} {b.booth}</span>}
              </td>
              <td className="p-2"
                  style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                {b.now ? fmtTime(b.now) : '—'}
                {b.next ? ` / ${fmtTime(b.next)}` : ''}
              </td>
              <td className="p-2"
                  style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                {b.done}</td>
              <td className="p-2"
                  style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                {b.no_show}</td>
              <td className="p-2"
                  style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                {b.free_slots}</td>
              <td className="p-2"
                  style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                {b.queue}</td>
              <td className="p-2"
                  style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                <button type="button" className="btn btn-secondary"
                        disabled={b.queue === 0 || b.free_slots === 0}
                        onClick={() => offer(b.employer_id)}>
                  {t('ev.org.day.offer')}
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

function Report({ id }: { id: string }) {
  const { t, lang } = useI18n()
  const langName = (c: string) => {
    try { return new Intl.DisplayNames([lang], { type: 'language' }).of(c) ?? c } catch { return c }
  }
  const [rep, setRep] = useState<OrganizerReport | null>(null)
  useEffect(() => {
    api<OrganizerReport>(`/api/advisor/events/${id}/report`)
      .then(setRep).catch(() => setRep(null))
  }, [id])
  if (!rep) return <p>{t('common.loading')}</p>
  const stages: [string, string][] = [
    ['registered', t('ev.org.fair.registered')],
    ['chose', t('ev.org.fair.chose')],
    ['invited', t('ev.org.fair.invited')],
    ['met', t('ev.org.fair.met')],
    ['next_step', t('ev.org.fair.next')],
  ]
  return (
    <div className="grid gap-4">
      <Section title={t('ev.org.rep.title')}>
        <div className="overflow-x-auto">
          <table className="w-full" style={{ borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {[t('ev.org.e'), t('ev.org.rep.booked'), t('ev.org.rep.held'),
                  t('ev.org.rep.noshow'), t('ev.org.rep.next')].map((h, i) => (
                  <th key={i} className="text-start p-2"
                      style={{ borderBottom: '2px solid var(--color-hairline)' }}>
                    {h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rep.booths.map((b) => (
                <tr key={b.employer_id}>
                  <td className="p-2"
                      style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                    {b.name}</td>
                  <td className="p-2"
                      style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                    {b.booked}</td>
                  <td className="p-2"
                      style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                    {b.held}</td>
                  <td className="p-2"
                      style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                    {b.no_show}</td>
                  <td className="p-2"
                      style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                    {b.next_step}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="m-0 ps-5 mt-2">
          <li>{t('ev.org.rep.cards', { n: rep.need_cards_on_time_pct ?? 0 })}</li>
          <li>{t('ev.org.rep.answers', { n: rep.answers_in_7d_pct ?? 0 })}</li>
        </ul>
      </Section>
      <Section title={t('ev.org.fair.title')}>
        <div className="overflow-x-auto">
          <table className="w-full" style={{ borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th className="text-start p-2"
                    style={{ borderBottom: '2px solid var(--color-hairline)' }}>
                  {t('ev.org.fair.lang')}</th>
                {stages.map(([k, label]) => (
                  <th key={k} className="text-start p-2"
                      style={{ borderBottom: '2px solid var(--color-hairline)' }}>
                    {label}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {rep.fairness.map((g) => (
                <tr key={g.card_language}>
                  <td className="p-2"
                      style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                    {langName(g.card_language)}</td>
                  {g.rates ? (
                    <>
                      <td className="p-2"
                          style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                        {g.registered}</td>
                      <td className="p-2"
                          style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                        {g.chose} ({g.rates.chose}%)</td>
                      <td className="p-2"
                          style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                        {g.invited} ({g.rates.invited}%)</td>
                      <td className="p-2"
                          style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                        {g.met} ({g.rates.met}%)</td>
                      <td className="p-2"
                          style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                        {g.next_step} ({g.rates.next_step}%)</td>
                    </>
                  ) : (
                    <td className="p-2" colSpan={5}
                        style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                      {g.registered} — {t('ev.org.fair.few')}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-secondary mt-2">{t('ev.org.fair.note')}</p>
      </Section>
    </div>
  )
}

export default function AdvisorEvent() {
  const { id } = useParams()
  const { t } = useI18n()
  const [board, setBoard] = useState<AdvisorBoard | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const [reminded, setReminded] = useState<Record<string, number>>({})
  const [fillFor, setFillFor] = useState('')
  const [draft, setDraft] = useState<NeedCardDraft>(EMPTY_NEED)
  const [busy, setBusy] = useState(false)
  const [formErr, setFormErr] = useState('')
  const now = useNow()

  const load = () => {
    setErr(null)
    api<AdvisorBoard>(`/api/advisor/events/${id}`).then(setBoard).catch(setErr)
  }
  useEffect(load, [id]) // eslint-disable-line react-hooks/exhaustive-deps

  if (err) return <ErrorState err={err} goneLabel={t('ev.gone')} retryLabel={t('err.retry')} onRetry={load} backTo="/advisor" backLabel={t('common.back')} />
  if (!board) return <p>{t('common.loading')}</p>
  const ev = board.event

  const remind = async (employerId: string) => {
    try {
      const d = await api<{ reminders_sent: number }>(
        `/api/advisor/events/${id}/remind`,
        { body: { employer_id: employerId } })
      setReminded({ ...reminded, [employerId]: d.reminders_sent })
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
      await api(`/api/advisor/events/${id}/need`,
        { method: 'PUT', body: { employer_id: fillFor, card } })
      setFillFor(''); setDraft(EMPTY_NEED); load()
    } catch (e2) {
      setFormErr(e2 instanceof ApiError ? e2.message : t('common.error'))
    } finally { setBusy(false) }
  }

  const before = (
    <div className="grid gap-6">
      <Section title={t('ev.org.talent')}>
        <div className="flex gap-4 flex-wrap">
          {Object.entries(board.talent.by_time_group).map(([g, n]) => (
            <span key={g} className="chip">
              {t('ev.org.group', { g, n })}
            </span>
          ))}
          <span className="chip">{t('ev.org.waitlist', { n: board.talent.waitlist })}</span>
          <span className="chip">{t('ev.org.mutual', { n: board.talent.mutual_matches })}</span>
          <span className="chip">{t('ev.org.meetings', { n: board.talent.meetings })}</span>
        </div>
      </Section>

      <Section title={t('ev.org.employers')}>
        {ev.need_deadline && (
          <p className="text-secondary">{t('ev.emp.deadline', { n: daysUntil(ev.need_deadline, now), d: fmtDate(ev.need_deadline) })}</p>
        )}
        <div className="overflow-x-auto">
          <table className="w-full" style={{ borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                {[t('ev.org.e'), t('ev.org.need'), t('ev.org.invites'), t('ev.org.booked'), ''].map((h, i) => (
                  <th key={i} className="text-start p-2"
                      style={{ borderBottom: '2px solid var(--color-hairline)' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {board.employers.map((e) => {
                const st = NEED_STYLE[e.need_status] ?? NEED_STYLE.missing
                return (
                  <tr key={e.employer_id}>
                    <td className="p-2" style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                      <strong>{e.name}</strong>
                      {e.contact_phone && (
                        <span className="block text-secondary">
                          <a href={`tel:${e.contact_phone}`}>{e.contact_phone}</a>
                        </span>
                      )}
                    </td>
                    <td className="p-2" style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                      <span className="chip" style={{ background: st.bg, color: st.fg }}>
                        {t(`ev.org.status.${e.need_status}` as Key)}
                      </span>
                      {e.need_by === 'advisor' && (
                        <span className="block text-secondary">{t('ev.byadvisor')}</span>
                      )}
                      {e.need_status !== 'missing' && e.need_submitted_at && (
                        <span className="block text-secondary">{fmtDate(e.need_submitted_at)}</span>
                      )}
                    </td>
                    <td className="p-2" style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                      {e.invites_used}/{e.slots}
                    </td>
                    <td className="p-2" style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                      {e.meetings}
                    </td>
                    <td className="p-2" style={{ borderBottom: '1px solid var(--color-hairline)' }}>
                      <div className="flex gap-2 flex-wrap">
                        <button type="button" className="btn btn-secondary"
                                style={{ flex: '1 1 140px' }}
                                onClick={() => remind(e.employer_id)}>
                          {t('ev.org.remind')}
                        </button>
                        <button type="button" className="btn btn-secondary"
                                style={{ flex: '1 1 140px' }}
                                onClick={() => { setFillFor(e.employer_id); setDraft(EMPTY_NEED) }}>
                          {t('ev.org.writefor')}
                        </button>
                      </div>
                      {(reminded[e.employer_id] ?? e.reminders_sent) > 0 && (
                        <span className="block text-secondary mt-1">
                          {t('ev.org.reminded', { n: reminded[e.employer_id] ?? e.reminders_sent })}
                        </span>
                      )}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
        <p className="text-secondary">{t('ev.org.remind.note')}</p>
      </Section>

      {fillFor && (
        <Section title={t('ev.org.writefor.title', {
          n: board.employers.find((e) => e.employer_id === fillFor)?.name ?? fillFor,
        })}>
          <NeedCardForm draft={draft} setDraft={setDraft} onSubmit={submitNeed}
                        busy={busy} err={formErr} jobs={[]}
                        submitLabel={t('ev.emp.need.send')} />
          <button type="button" className="btn btn-secondary mt-2"
                  onClick={() => setFillFor('')}>{t('common.cancel')}</button>
        </Section>
      )}
    </div>
  )

  const day = (
    <div className="grid gap-4">
      <LiveBoard id={id!} />
    </div>
  )

  const after = (
    <div className="grid gap-3">
      <p><Link to="/advisor/follow-up" style={{ color: 'var(--color-brand)' }}>
        {t('ev.org.followup')}
      </Link></p>
      <Report id={id!} />
    </div>
  )

  return (
    <div className="grid gap-4">
      <div>
        <h1 data-page-title tabIndex={-1} className="mb-1">{ev.name}</h1>
        <p className="m-0">{fmtDate(ev.date)} · {fmtTime(ev.starts_at)}–{fmtTime(ev.ends_at)} · {ev.venue}</p>
        <p className="m-0 text-secondary">{t(`ev.phase.${ev.phase}` as Key)}</p>
        <p className="m-0 text-secondary">
          {ev.matching_closes &&
            `${t('ev.org.matchby')} ${fmtDate(ev.matching_closes.slice(0, 10))}`}
          {ev.answers_due &&
            ` · ${t('ev.org.ansby')} ${fmtDate(ev.answers_due.slice(0, 10))}`}
        </p>
      </div>
      <Tabs label={ev.name}
            initial={ev.phase === 'live' ? 1 : (ev.phase === 'after' || ev.phase === 'closed') ? 2 : 0}
            labels={[t('ev.tab.before'), t('ev.tab.day'), t('ev.tab.after')]}>
        {[before, day, after]}
      </Tabs>
    </div>
  )
}
