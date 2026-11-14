import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Catalog, Connection, MyBadge, Profile } from '../types'
import { CEFR, DAYS, PARTS } from '../types'
import { ErrorBox, Field, Section, Toggle } from '../components/ui'

const DOC_SUGGESTIONS = [
  'Hygiene passport (hygieniapassi)', 'Hot work card (tulityökortti)',
  'Occupational safety card (työturvallisuuskortti)', 'Driving licence C',
  'Driving licence D', 'Valvira registration', 'First aid EA1',
  'Welding certificate',
]

export default function ProfilePage() {
  const { t } = useI18n()
  const { logout } = useAuth()
  const nav = useNavigate()
  const [p, setP] = useState<Profile | null>(null)
  const [creds, setCreds] = useState<{ id: string; label: string; checked_at: string }[]>([])
  const [docLabel, setDocLabel] = useState('')
  const [docBusy, setDocBusy] = useState(false)
  const [docSent, setDocSent] = useState(false)
  const loadCreds = () => api<{ credentials: typeof creds }>('/api/me/credentials')
    .then((r) => setCreds(r.credentials)).catch(() => undefined)
  const delCred = async (id: string) => {
    await api(`/api/me/credentials/${id}`, { method: 'DELETE' }).catch(() => undefined)
    loadCreds()
  }
  const sendDocRequest = async () => {
    setDocBusy(true)
    try {
      await api('/api/help-requests', { body: {
        kind: 'check_document', document_label: docLabel.trim(),
        consent: true, message: docLabel.trim() } })
      setDocSent(true); setDocLabel('')
    } catch { /* consent/contact validation surfaces on the help page */ }
    setDocBusy(false)
  }
  const [cat, setCat] = useState<Catalog | null>(null)
  const [badges, setBadges] = useState<MyBadge[]>([])
  const [conns, setConns] = useState<Connection[]>([])
  const [err, setErr] = useState('')
  const [savedMsg, setSavedMsg] = useState('')
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [setup, setSetup] = useState<number | null>(null)

  useEffect(() => { loadCreds() }, []) // eslint-disable-line react-hooks/exhaustive-deps
  useEffect(() => {
    api<Profile>('/api/me/profile').then((pr) => {
      setP(pr)
      if (!pr.contact_method && !pr.availability.length
          && !pr.needs.length && !pr.languages.length) {
        setSetup(0)
      }
    }).catch((e) => setErr(e instanceof ApiError ? e.message : t('common.error')))
    api<Catalog>('/api/catalog').then(setCat).catch(() => {})
    api<{ badges: MyBadge[] }>('/api/me/badges')
      .then((d) => setBadges(d.badges)).catch(() => {})
    api<{ connections: Connection[] }>('/api/me/connections')
      .then((d) => setConns(d.connections)).catch(() => {})
  }, [t])

  if (!p) return <p>{err || t('common.loading')}</p>

  const patch = async (body: Partial<Profile>) => {
    setErr(''); setSavedMsg('')
    try {
      const np = await api<Profile>('/api/me/profile', { body })
      setP(np); setSavedMsg(t('profile.saved'))
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }
  const toggleIn = (list: string[], k: string) =>
    list.includes(k) ? list.filter((x) => x !== k) : [...list, k]

  const download = async () => {
    const data = await api<Record<string, unknown>>('/api/me/export')
    const blob = new Blob([JSON.stringify(data, null, 2)],
      { type: 'application/json' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'espoo-work-map-data.json'
    a.click()
    URL.revokeObjectURL(a.href)
  }
  const remove = async () => {
    await api('/api/me', { method: 'DELETE' })
    logout()
    nav('/sign-in')
  }

  const slotSet = new Set(p.availability)

  // 4-step skippable first-visit setup
  if (setup != null) {
    const stepTitle = [
      t('profile.contact'), t('profile.availability'),
      t('profile.needs'), t('profile.languages'),
    ][setup]
    return (
      <div className="max-w-2xl mx-auto">
        <h1 data-page-title tabIndex={-1}>{t('profile.firstvisit')}</h1>
        <p className="text-secondary">{t('profile.setup')}</p>
        <div className="flex gap-2 mb-4" aria-hidden="true">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="flex-1 rounded-full" style={{
              height: 8,
              background: i <= setup ? 'var(--color-ink)' : 'var(--color-hairline)',
            }} />
          ))}
        </div>
        <p className="font-medium">{t('profile.setupstep')} {setup + 1} / 4 — {stepTitle}</p>
        <p className="text-secondary" style={{ fontSize: '1rem' }}>
          {t('profile.setup')} {t('profile.skip')}
        </p>
        <div className="card p-5">
          {setup === 0 && (
            <>
              <div className="flex gap-2 mb-3">
                {(['phone', 'sms', 'email'] as const).map((m) => (
                  <Toggle key={m} pressed={p.contact_method === m}
                          onClick={() => setP({ ...p, contact_method: m })}>
                    {t(`apply.${m}` as Key)}
                  </Toggle>
                ))}
              </div>
              <Field label={t('profile.area')} id="sw-district">
                <select id="sw-district" value={p.district ?? ''}
                        onChange={(e) => setP({ ...p, district: e.target.value || null })}>
                  <option value="">—</option>
                  {cat?.districts.map((d) => (
                    <option key={d.id} value={d.id}>{d.name}</option>
                  ))}
                </select>
              </Field>
            </>
          )}
          {setup === 1 && (
            <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
              <div />
              {PARTS.map((x) => <strong key={x}>{t(`part.${x}` as Key)}</strong>)}
              {DAYS.map((d) => (
                <div key={d} className="contents">
                  <strong className="self-center">{t(`dayfull.${d}` as Key)}</strong>
                  {PARTS.map((x) => {
                    const s = `${d}-${x}`
                    return (
                      <Toggle key={s} pressed={slotSet.has(s)}
                              onClick={() => setP({ ...p, availability: toggleIn(p.availability, s) })}
                              className="justify-center">
                        {t(`part.${x}` as Key)}
                      </Toggle>
                    )
                  })}
                </div>
              ))}
            </div>
          )}
          {setup === 2 && (
            <>
              <p className="text-secondary mt-0">{t('profile.needshint')}</p>
              <div className="flex flex-wrap gap-2">
                {cat?.condition_keys.map((c) => (
                  <Toggle key={c.id} pressed={p.needs.includes(c.id)}
                          onClick={() => setP({ ...p, needs: toggleIn(p.needs, c.id) })}>
                    {t(`cond.${c.id}` as Key)}
                  </Toggle>
                ))}
              </div>
            </>
          )}
          {setup === 3 && (
            <Field label={t('profile.about')} id="sw-about">
              <textarea id="sw-about" value={p.about ?? ''}
                        onChange={(e) => setP({ ...p, about: e.target.value })} />
            </Field>
          )}
        </div>
        <div className="flex gap-2 mt-4">
          <button type="button" className="btn btn-secondary flex-1"
                  onClick={() => setSetup(null)}>
            {t('profile.skip')}
          </button>
          <button type="button" className="btn btn-primary flex-1"
                  onClick={() => {
                    if (setup < 3) setSetup(setup + 1)
                    else { setSetup(null); patch(p) }
                  }}>
            {setup < 3 ? t('common.next') : t('profile.save')}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('profile.title')}</h1>
      {err && <ErrorBox>{err}</ErrorBox>}
      {savedMsg && <p role="status" className="card p-3" aria-live="polite">{savedMsg}</p>}
      <p className="text-secondary">{t('profile.explain')}</p>

      <Section title={t('profile.contact')}>
        <div className="flex gap-2 mb-3">
          {(['phone', 'sms', 'email'] as const).map((m) => (
            <Toggle key={m} pressed={p.contact_method === m}
                    onClick={() => setP({ ...p, contact_method: m })}>
              {t(`apply.${m}` as Key)}
            </Toggle>
          ))}
        </div>
        <Field label={t('apply.value')} id="pf-value">
          <input id="pf-value"
                 value={p.contact_method === 'email' ? p.email ?? '' : p.phone ?? ''}
                 onChange={(e) => setP({
                   ...p,
                   [p.contact_method === 'email' ? 'email' : 'phone']: e.target.value,
                 })} />
        </Field>
        <Field label={t('profile.about')} id="pf-about">
          <textarea id="pf-about" value={p.about ?? ''}
                    onChange={(e) => setP({ ...p, about: e.target.value })} />
        </Field>
      </Section>

      <Section title={t('profile.district')}>
        <Field label={t('jobs.area')} id="pf-district">
          <select id="pf-district" value={p.district ?? ''}
                  onChange={(e) => setP({ ...p, district: e.target.value || null })}>
            <option value="">—</option>
            {cat?.districts.map((d) => (
              <option key={d.id} value={d.id}>{d.name}</option>
            ))}
          </select>
        </Field>
        <Field label={t('profile.fields')} id="pf-fields">
          <div className="flex flex-wrap gap-2">
            {cat?.fields.map((f) => (
              <Toggle key={f.id} pressed={p.fields.includes(f.id)}
                      onClick={() => setP({ ...p, fields: toggleIn(p.fields, f.id) })}>
                {f.name}
              </Toggle>
            ))}
          </div>
        </Field>
        <Field label={t('profile.maxhours')} id="pf-hours">
          <input id="pf-hours" type="number" min="1" inputMode="numeric"
                 value={p.max_hours_per_week ?? ''}
                 onChange={(e) => setP({
                   ...p,
                   max_hours_per_week: e.target.value ? +e.target.value : null,
                 })} />
        </Field>
      </Section>

      <Section title={t('profile.availability')}>
        <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
          <div />
          {PARTS.map((x) => <strong key={x}>{t(`part.${x}` as Key)}</strong>)}
          {DAYS.map((d) => (
            <div key={d} className="contents">
              <strong className="self-center">{t(`dayfull.${d}` as Key)}</strong>
              {PARTS.map((x) => {
                const s = `${d}-${x}`
                return (
                  <Toggle key={s} pressed={slotSet.has(s)}
                          onClick={() => setP({ ...p, availability: toggleIn(p.availability, s) })}
                          className="justify-center">
                    {t(`part.${x}` as Key)}
                  </Toggle>
                )
              })}
            </div>
          ))}
        </div>
      </Section>

      <Section title={t('profile.needs')}>
        <p className="text-secondary mt-0">{t('profile.needsexplain')}</p>
        <div className="flex flex-wrap gap-2">
          {cat?.condition_keys.map((c) => (
            <Toggle key={c.id} pressed={p.needs.includes(c.id)}
                    onClick={() => setP({ ...p, needs: toggleIn(p.needs, c.id) })}>
              {t(`cond.${c.id}` as Key)}
            </Toggle>
          ))}
        </div>
      </Section>

      <Section title={t('profile.languages')}>
        {p.languages.map((l, i) => (
          <div key={i} className="flex gap-2 mb-2 items-center">
            <input value={l.language} aria-label={t('jobs.language')}
                   onChange={(e) => setP({
                     ...p,
                     languages: p.languages.map((x, j) =>
                       j === i ? { ...x, language: e.target.value } : x),
                   })} />
            <select value={l.level} aria-label={t('jobs.mylevel')}
                    onChange={(e) => setP({
                      ...p,
                      languages: p.languages.map((x, j) =>
                        j === i ? { ...x, level: e.target.value } : x),
                    })}>
              {CEFR.map((c) => <option key={c} value={c}>{c}</option>)}
            </select>
            <button type="button" className="btn btn-quiet" style={{ minHeight: 40 }}
                    onClick={() => setP({ ...p, languages: p.languages.filter((_, j) => j !== i) })}
                    aria-label={t('common.delete')}>✕</button>
          </div>
        ))}
        <button type="button" className="btn btn-secondary"
                onClick={() => setP({ ...p, languages: [...p.languages, { language: '', level: 'B1' }] })}>
          {t('profile.addlang')}
        </button>
      </Section>

      <Section title={t('profile.share')}>
        <p className="text-secondary mt-0">{t('profile.share.hint')}</p>
        <div className="grid gap-2">
          <Toggle pressed={p.share_email}
                  onClick={() => setP({ ...p, share_email: !p.share_email })}>
            {t('profile.share.email')}
          </Toggle>
          <Toggle pressed={p.share_phone}
                  onClick={() => setP({ ...p, share_phone: !p.share_phone })}>
            {t('profile.share.phone')}
          </Toggle>
          <Field label={t('profile.share.link')} id="pf-link">
            <input id="pf-link" value={p.public_link ?? ''}
                   placeholder="https://"
                   onChange={(e) => setP({ ...p, public_link: e.target.value })} />
          </Field>
        </div>
      </Section>

      <button type="button" className="btn btn-primary w-full"
              onClick={() => patch(p)}>{t('profile.save')}</button>

      <Section title={t('profile.badges')}>
        {badges.length === 0 ? (
          <p className="text-secondary">{t('profile.badges.none')}</p>
        ) : (
          <ul className="m-0 p-0 list-none grid gap-2">
            {badges.map((b) => (
              <li key={b.id} className="card p-3 flex flex-wrap gap-2 items-center">
                <span className="font-medium">
                  {b.kind === 'attended'
                    ? t('badge.attended', { event: b.event_name })
                    : t(`badge.${b.label}` as Key)}
                </span>
                {b.giver_name &&
                  <span className="text-secondary"> — {b.giver_name}</span>}
                <button type="button" className="btn btn-quiet ms-auto"
                        style={{ minHeight: 40 }}
                        onClick={async () => {
                          await api(`/api/me/badges/${b.id}/hide`,
                                    { method: 'PUT',
                                      body: { hidden: !b.hidden } })
                          setBadges(badges.map((x) =>
                            x.id === b.id ? { ...x, hidden: !x.hidden } : x))
                        }}>
                  {b.hidden ? t('badge.show') : t('badge.hide')}
                </button>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title={t('profile.connections')}>
        {conns.length === 0 ? (
          <p className="text-secondary">{t('profile.connections.none')}</p>
        ) : (
          <ul className="m-0 p-0 list-none grid gap-2">
            {conns.map((c) => (
              <li key={`${c.event_id}-${c.user_id}`}
                  className="card p-3 flex flex-wrap gap-2 items-center">
                <div>
                  <strong>{c.name}</strong>
                  {c.company &&
                    <span className="text-secondary"> — {c.company}</span>}
                  <span className="block text-secondary">{c.event_name}</span>
                  {(c.email || c.phone || c.public_link) && (
                    <span className="block">
                      {[c.email, c.phone, c.public_link]
                        .filter(Boolean).join(' · ')}</span>
                  )}
                </div>
                <button type="button" className="btn btn-quiet ms-auto"
                        style={{ minHeight: 40 }}
                        onClick={async () => {
                          await api(`/api/me/connections/${c.event_id}/${c.user_id}`,
                                    { method: 'DELETE' })
                          setConns(conns.filter((x) =>
                            !(x.event_id === c.event_id
                              && x.user_id === c.user_id)))
                        }}>
                  {t('conn.remove')}
                </button>
              </li>
            ))}
          </ul>
        )}
      </Section>

      <Section title={t('profile.documents')}>
        <div id="documents" />
        <p className="text-secondary mt-0">{t('profile.documents.hint')}</p>
        {creds.length > 0 && (
          <ul className="m-0 mb-3 p-0 list-none grid gap-2">
            {creds.map((c) => (
              <li key={c.id} className="flex flex-wrap items-center gap-2 card p-3">
                <span className="font-medium">{c.label}</span>
                <span className="text-secondary">
                  {t('profile.documents.seen', { d: c.checked_at })}
                </span>
                <button type="button" className="btn btn-quiet"
                        onClick={() => delCred(c.id)}>
                  {t('common.delete')}
                </button>
              </li>
            ))}
          </ul>
        )}
        <Field label={t('profile.documents.label')} id="doc-label">
          <input id="doc-label" value={docLabel} list="doc-suggestions"
                 onChange={(e) => setDocLabel(e.target.value)} />
          <datalist id="doc-suggestions">
            {DOC_SUGGESTIONS.map((d) => <option key={d} value={d} />)}
          </datalist>
        </Field>
        <p className="text-secondary mt-2">{t('profile.documents.how')}</p>
        <button type="button" className="btn btn-secondary" disabled={!docLabel.trim() || docBusy}
                onClick={sendDocRequest}>
          {t('profile.documents.send')}
        </button>
        {docSent && <p role="status" className="mt-2">{t('profile.documents.sent')}</p>}
      </Section>

      <Section title={t('profile.data')}>
        <div className="flex flex-wrap gap-2">
          <button type="button" className="btn btn-secondary" onClick={download}>
            {t('profile.download')}
          </button>
          <button type="button" className="btn btn-danger"
                  onClick={() => setConfirmDelete(true)}>
            {t('profile.delete')}
          </button>
        </div>
        {confirmDelete && (
          <div className="card p-4 mt-4" role="alertdialog"
               aria-label={t('profile.deletetitle')}>
            <p className="mt-0">{t('profile.deleteexplain')}</p>
            <div className="flex gap-2">
              <button type="button" className="btn btn-secondary"
                      onClick={() => setConfirmDelete(false)}>
                {t('common.back')}
              </button>
              <button type="button" className="btn btn-danger" onClick={remove}>
                {t('profile.delete')}
              </button>
            </div>
          </div>
        )}
      </Section>
    </div>
  )
}
