import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import { ErrorBox, Section } from '../components/ui'

const KUDOS = ['explains_clearly', 'solved_task', 'customer_focus',
               'team_player', 'learns_fast', 'reliable', 'helped_others']

type Badge = { id: string; kind: string; label: string; note: string
              event_name?: string; giver_name?: string | null }
type Profile = {
  role: string; first_name: string; name?: string; company?: string
  event_id: string; event_name: string; viewer_employer: boolean
  looking_for?: string; done?: { text: string }[] | string[]
  credentials?: string[]; badges: Badge[]
  event_records?: { employer: string; date: string; observed: string[] }[]
  need_card?: { first_week?: string[]; looking_for?: string } | null
  contact: { email?: string; phone?: string; public_link?: string }
  user_id?: string
}

function BadgeRow({ b }: { b: Badge }) {
  const { t } = useI18n()
  const label = b.kind === 'attended'
    ? t('badge.attended', { event: b.event_name ?? '' })
    : t(`badge.${b.label}` as Key)
  return (
    <li className="card p-3">
      <strong>{label}</strong>
      {b.giver_name &&
        <span className="text-secondary"> — {b.giver_name}
          {b.event_name ? ` · ${b.event_name}` : ''}</span>}
      {b.note && <span className="block">{b.note}</span>}
    </li>
  )
}

/** What the scanner sees after reading a QR pass. */
export default function PersonProfile() {
  const { token } = useParams()
  const { t } = useI18n()
  const { user } = useAuth()
  const [p, setP] = useState<Profile | null>(null)
  const [err, setErr] = useState('')
  const [badgeOpen, setBadgeOpen] = useState(false)
  const [label, setLabel] = useState(KUDOS[0])
  const [note, setNote] = useState('')
  const [msg, setMsg] = useState('')
  const [ownNote, setOwnNote] = useState('')

  useEffect(() => {
    if (!user) return
    api<Profile>(`/api/p/${token}`).then(setP)
      .catch((e) => setErr(e instanceof ApiError ? e.message
                           : t('common.error')))
  }, [user, token, t])

  if (!user) {
    return (
      <div className="grid gap-3">
        <h1 data-page-title tabIndex={-1}>{t('p.signin.title')}</h1>
        <p className="max-w-prose">{t('p.signin.why')}</p>
        <p><Link className="btn btn-primary inline-block"
                 to={`/sign-in?next=/p/${token}`}>{t('nav.signin')}</Link></p>
      </div>
    )
  }
  if (err) return <ErrorBox>{err}</ErrorBox>
  if (!p) return <p>{t('common.loading')}</p>

  const act = async (fn: () => Promise<unknown>, ok: string) => {
    setMsg('')
    try { await fn(); setMsg(ok) }
    catch (e) {
      setMsg(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  return (
    <div className="grid gap-4">
      <div>
        <h1 data-page-title tabIndex={-1} className="mb-1">
          {p.role === 'employer' ? p.name : p.first_name}</h1>
        <p className="m-0 text-secondary">{p.event_name}</p>
        {p.company && <p className="m-0">{p.company}</p>}
      </div>

      {p.role === 'resident' && (
        <>
          {p.looking_for &&
            <p className="card p-3 m-0 max-w-prose">{p.looking_for}</p>}
          {(p.done ?? []).length > 0 && (
            <Section title={t('p.done')}>
              <ul className="m-0 ps-5">
                {(p.done as { text?: string }[]).map((d, i) =>
                  <li key={i}>{typeof d === 'string' ? d : d.text}</li>)}
              </ul>
            </Section>
          )}
          {(p.credentials ?? []).length > 0 && (
            <Section title={t('p.docs')}>
              <ul className="m-0 ps-5">
                {p.credentials!.map((c) => <li key={c}>{c}</li>)}
              </ul>
            </Section>
          )}
        </>
      )}
      {p.role === 'employer' && p.need_card?.first_week && (
        <Section title={t('ev.firstweek')}>
          <ul className="m-0 ps-5">
            {p.need_card.first_week.map((x, i) => <li key={i}>{x}</li>)}
          </ul>
        </Section>
      )}

      {p.badges.length > 0 && (
        <Section title={t('p.badges')}>
          <ul className="grid gap-2 p-0 list-none">
            {p.badges.map((b, i) => <BadgeRow key={b.id ?? i} b={b} />)}
          </ul>
        </Section>
      )}

      {(p.event_records ?? []).length > 0 && (
        <Section title={t('ev.after.seen')}>
          <ul className="grid gap-2 p-0 list-none">
            {p.event_records!.map((r, i) => (
              <li key={i} className="card p-3">
                <strong>{r.employer}</strong>
                <ul className="m-0 ps-5">
                  {r.observed.map((o, j) => <li key={j}>{o}</li>)}
                </ul>
              </li>
            ))}
          </ul>
        </Section>
      )}

      {(p.contact.email || p.contact.phone || p.contact.public_link) && (
        <Section title={t('p.contact')}>
          <ul className="m-0 p-0 list-none grid gap-1">
            {p.contact.email && <li>{p.contact.email}</li>}
            {p.contact.phone && <li>{p.contact.phone}</li>}
            {p.contact.public_link &&
              <li><a href={p.contact.public_link}>{p.contact.public_link}</a></li>}
          </ul>
        </Section>
      )}

      {p.viewer_employer && p.role === 'resident' && (
        <Section title={t('p.actions')}>
          <div className="grid gap-2" style={{ maxWidth: 360 }}>
            <button type="button" className="btn btn-primary"
                    onClick={() => act(() =>
                      api(`/api/employer/events/${p.event_id}/talk`,
                          { method: 'POST',
                            body: { user_id: p.user_id } }),
                      t('p.talk.saved'))}>
              {t('p.action.talk')}</button>
            <button type="button" className="btn btn-quiet"
                    onClick={() => setBadgeOpen((v) => !v)}>
              {t('p.action.badge')}</button>
            {badgeOpen && (
              <div className="card p-3 grid gap-2">
                <div className="grid gap-1">
                  {KUDOS.map((k) => (
                    <label key={k} className="flex gap-2 items-center">
                      <input type="radio" name="kudos" checked={label === k}
                             onChange={() => setLabel(k)} />
                      {t(`badge.${k}` as Key)}
                    </label>
                  ))}
                </div>
                <label className="grid gap-1">
                  <span>{t('p.badge.note')}</span>
                  <input className="input" value={note} maxLength={140}
                         onChange={(e) => setNote(e.target.value)} />
                </label>
                <button type="button" className="btn btn-primary"
                        onClick={() => act(() =>
                          api(`/api/employer/events/${p.event_id}/kudos`,
                              { method: 'POST', body: {
                                user_id: p.user_id, label,
                                note: note || undefined } }),
                          t('p.badge.saved'))}>
                  {t('p.badge.give')}</button>
              </div>
            )}
            <label className="grid gap-1">
              <span>{t('p.note.own')}</span>
              <input className="input" value={ownNote} maxLength={140}
                     placeholder={t('p.note.ph')}
                     onChange={(e) => setOwnNote(e.target.value)}
                     onBlur={() => ownNote && act(() =>
                       api(`/api/me/connections/${p.event_id}/${p.user_id}/note`,
                           { method: 'PUT', body: { note: ownNote } }),
                       t('p.note.saved'))} />
            </label>
          </div>
        </Section>
      )}
      {msg && <ErrorBox>{msg}</ErrorBox>}
    </div>
  )
}
