import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Catalog, HelpRequest, Job } from '../types'
import { ErrorBox, Field, Section, Toggle } from '../components/ui'
import VoiceInput from '../components/VoiceInput'

const KINDS = ['check_conditions', 'prepare_application', 'arrange_contact', 'other'] as const

export default function Help() {
  const { t } = useI18n()
  const { user } = useAuth()
  const [params] = useSearchParams()
  const jobId = params.get('job')
  const [job, setJob] = useState<Job | null>(null)
  const [cat, setCat] = useState<Catalog | null>(null)
  const [kind, setKind] = useState<(typeof KINDS)[number]>(
    params.get('keys') ? 'check_conditions' : 'other')
  const [keys, setKeys] = useState<Set<string>>(
    new Set((params.get('keys') || '').split(',').filter(Boolean)))
  const [message, setMessage] = useState(() =>
    params.get('q') ? t('help.prefill.q', { q: params.get('q')! }) : '')
  const jobIds = params.get('jobs')
  useEffect(() => {
    if (!jobIds) return
    Promise.all(jobIds.split(',').map((id) =>
      api<Job>(`/api/jobs/${id}`).catch(() => null))).then((js) => {
      const titles = js.filter(Boolean).map((j) => j!.title).join(' + ')
      if (titles) setMessage(t('help.prefill.jobs', { jobs: titles }))
    })
  }, [jobIds, t])
  const [name, setName] = useState('')
  const [method, setMethod] = useState<'phone' | 'sms' | 'email'>('phone')
  const [value, setValue] = useState('')
  const [consent, setConsent] = useState(false)
  const [err, setErr] = useState('')
  const [busy, setBusy] = useState(false)
  const [sent, setSent] = useState(false)

  useEffect(() => {
    api<Catalog>('/api/catalog').then(setCat).catch(() => {})
    if (jobId) api<Job>(`/api/jobs/${jobId}`).then(setJob).catch(() => {})
  }, [jobId])

  const unknownKeys = job
    ? job.conditions.filter((c) => c.value === 'unknown').map((c) => c.key)
    : []

  const submit = async () => {
    setBusy(true); setErr('')
    try {
      await api<HelpRequest>('/api/help-requests', {
        body: {
          job_id: jobId || undefined, kind,
          condition_keys: kind === 'check_conditions' ? [...keys] : [],
          message, consent,
          name: user ? undefined : name,
          contact_method: method, contact_value: value,
        },
      })
      setSent(true)
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    } finally {
      setBusy(false)
    }
  }

  if (sent) {
    return (
      <div className="card p-6 max-w-xl mx-auto text-center">
        <h1 data-page-title tabIndex={-1}>{t('help.sent')}</h1>
        <p>{t('help.sentbody')}</p>
        <p className="text-secondary">{t('help.phone')}</p>
        <Link to="/jobs" className="btn btn-primary mt-2">{t('nav.jobs')}</Link>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('help.title')}</h1>
      {err && <ErrorBox>{err}</ErrorBox>}

      <Section title={t('help.what')}>
        <div className="grid gap-2" role="radiogroup" aria-label={t('help.what')}>
          {KINDS.map((k) => (
            <label key={k} className={`btn ${kind === k ? 'btn-primary' : 'btn-quiet'} justify-start text-start gap-3`}
                   style={{ minHeight: 48, justifyContent: 'flex-start' }}>
              <input type="radio" name="help-kind" checked={kind === k}
                     onChange={() => setKind(k)} style={{ width: 20, height: 20 }} />
              {t(`help.kind.${k}` as Key)}
            </label>
          ))}
        </div>
      </Section>

      {job && (
        <p className="card p-4 text-secondary">
          {job.title} — {job.employer?.name}
        </p>
      )}

      {kind === 'check_conditions' && cat && (
        <Section title={t('help.which')}>
          <div className="flex flex-wrap gap-2">
            {(unknownKeys.length ? unknownKeys
              : cat.condition_keys.map((c) => c.id)).map((k) => (
              <Toggle key={k} pressed={keys.has(k)}
                      onClick={() => setKeys((s) => {
                        const n = new Set(s)
                        if (n.has(k)) n.delete(k); else n.add(k)
                        return n
                      })}>
                {t(`cond.${k}` as Key)}
              </Toggle>
            ))}
          </div>
        </Section>
      )}

      <Section title={t('help.message')}>
        <Field label={t('help.message')} id="help-msg">
          <textarea id="help-msg" value={message}
                    onChange={(e) => setMessage(e.target.value)} />
        </Field>
        <VoiceInput targetId="help-msg"
                    onText={(txt) => setMessage((m) => (m ? `${m} ` : '') + txt)} />
      </Section>

      <Section title={t('help.contact')}>
        {!user && (
          <Field label={t('help.name')} id="help-name">
            <input id="help-name" value={name}
                   onChange={(e) => setName(e.target.value)} required />
          </Field>
        )}
        <div className="flex gap-2 my-3">
          {(['phone', 'sms', 'email'] as const).map((m) => (
            <Toggle key={m} pressed={method === m} onClick={() => setMethod(m)}>
              {t(`apply.${m}` as Key)}
            </Toggle>
          ))}
        </div>
        <Field label={t('apply.value')} id="help-value">
          <input id="help-value" value={value}
                 onChange={(e) => setValue(e.target.value)} />
        </Field>
      </Section>

      <label className="card p-4 flex items-start gap-3 mb-5" style={{ minHeight: 52 }}>
        <input type="checkbox" checked={consent}
               onChange={(e) => setConsent(e.target.checked)}
               className="mt-1" style={{ width: 22, height: 22 }} />
        <span>{t('help.consent')}</span>
      </label>

      <button type="button" className="btn btn-primary w-full" disabled={busy}
              onClick={submit}>
        {t('common.send')}
      </button>
      <p className="text-secondary text-center mt-3">{t('help.phone')}</p>
    </div>
  )
}
