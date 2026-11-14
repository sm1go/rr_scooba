import { useEffect, useState } from 'react'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { EmployerProfile } from '../../types'
import { ErrorBox, Field, Section, Toggle } from '../../components/ui'
import type { Key } from '../../i18n/en'

export default function EmployerCompany() {
  const { t } = useI18n()
  const [p, setP] = useState<EmployerProfile | null>(null)
  const [err, setErr] = useState('')
  const [savedMsg, setSavedMsg] = useState('')

  useEffect(() => {
    api<EmployerProfile>('/api/employer').then(setP)
      .catch((e) => setErr(e instanceof ApiError ? e.message : t('common.error')))
  }, [t])

  if (!p) return <p>{err || t('common.loading')}</p>
  const save = async () => {
    setErr(''); setSavedMsg('')
    try {
      setP(await api<EmployerProfile>('/api/employer', { method: 'PUT', body: p }))
      setSavedMsg(t('profile.saved'))
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('employer.company')}</h1>
      {err && <ErrorBox>{err}</ErrorBox>}
      {savedMsg && <p role="status" className="card p-3" aria-live="polite">{savedMsg}</p>}

      <Section title={t('employer.company')}>
        <Field label={t('employer.companyname')} id="ec-name">
          <input id="ec-name" value={p.name}
                 onChange={(e) => setP({ ...p, name: e.target.value })} />
        </Field>
        <Field label={t('employer.about')} id="ec-about">
          <textarea id="ec-about" value={p.about}
                    onChange={(e) => setP({ ...p, about: e.target.value })} />
        </Field>
      </Section>

      <Section title={t('employer.contact')}>
        <Field label={t('auth.name')} id="ec-cn">
          <input id="ec-cn" value={p.contact_name}
                 onChange={(e) => setP({ ...p, contact_name: e.target.value })} />
        </Field>
        <Field label={t('auth.email')} id="ec-ce">
          <input id="ec-ce" type="email" value={p.contact_email}
                 onChange={(e) => setP({ ...p, contact_email: e.target.value })} />
        </Field>
        <Field label={t('employer.phone')} id="ec-cp">
          <input id="ec-cp" value={p.contact_phone}
                 onChange={(e) => setP({ ...p, contact_phone: e.target.value })} />
        </Field>
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
          <Field label={t('profile.share.link')} id="ec-link">
            <input id="ec-link" value={p.public_link ?? ''}
                   placeholder="https://"
                   onChange={(e) => setP({ ...p, public_link: e.target.value })} />
          </Field>
        </div>
      </Section>

      {(p.badges ?? []).length > 0 && (
        <Section title={t('profile.badges')}>
          <ul className="m-0 p-0 list-none grid gap-2">
            {p.badges.map((b) => (
              <li key={b.id} className="card p-3">
                {t(`badge.${b.label}` as Key)}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {p.event && (
        <Section title={t('employer.event')}>
          <p className="m-0">{p.event.name} — {p.event.date}</p>
          <p className="m-0 text-secondary">
            {p.event.venue} · {t('job.booth')} {p.event.booth}
          </p>
        </Section>
      )}

      <button type="button" className="btn btn-primary" onClick={save}>
        {t('profile.save')}
      </button>
    </div>
  )
}
