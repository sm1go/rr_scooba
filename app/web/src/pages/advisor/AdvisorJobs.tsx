import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { Condition, Job } from '../../types'
import { ErrorBox, Field, Section, Toggle } from '../../components/ui'
import JobsPage from '../Jobs'

/** Advisor browse: the same list + map + filters residents see,
    plus advisor actions on each row. */
export function AdvisorJobs() {
  const { t } = useI18n()
  return (
    <JobsPage
      headerExtra={
        <div className="flex gap-2 flex-wrap">
          <Link to="/advisor/jobs/new?start=photo" className="btn btn-secondary">
            {t('advisor.photoadd')}
          </Link>
          <Link to="/advisor/note" className="btn btn-secondary">
            {t('advisor.newnote')}
          </Link>
          <Link to="/advisor/jobs/new" className="btn btn-primary">
            {t('employer.addjob')}
          </Link>
        </div>
      }
      rowActions={(j) => (
        <div className="flex gap-2 mt-3 flex-wrap">
          <Link to={`/advisor/jobs/${j.id}/check`} className="btn btn-secondary"
                style={{ minHeight: 44 }}>
            {t('job.askcheck')}
          </Link>
          <Link to={`/advisor/jobs/${j.id}/call`} className="btn btn-secondary"
                style={{ minHeight: 44 }}>
            {t('advisor.callscript')}
          </Link>
          <Link to={`/advisor/jobs/${j.id}/edit`} className="btn btn-secondary"
                style={{ minHeight: 44 }}>
            {t('common.edit')}
          </Link>
          <Link to={`/advisor/jobs/${j.id}/apply-for`} className="btn btn-secondary"
                style={{ minHeight: 44 }}>
            {t('advisor.applyfor')}
          </Link>
        </div>
      )}
    />
  )
}

/** Advisor checks a job's conditions → serialized output changes
    (source 'advisor' + checked date). */
export function AdvisorJobCheck() {
  const { t } = useI18n()
  const { id } = useParams()
  const [job, setJob] = useState<Job | null>(null)
  const [err, setErr] = useState('')
  const [notes, setNotes] = useState<Record<string, string>>({})

  const load = () => {
    api<Job>(`/api/jobs/${id}`).then(setJob)
      .catch((e) => setErr(e instanceof ApiError ? e.message : t('common.error')))
  }
  useEffect(load, [id, t])

  const check = async (c: Condition, value: 'yes' | 'no') => {
    try {
      await api(`/api/advisor/jobs/${job!.id}/conditions`, {
        method: 'PUT',
        body: { key: c.key, value, note: notes[c.key] ?? '' },
      })
      load()
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  if (!job) return <p>{err || t('common.loading')}</p>
  return (
    <div className="max-w-3xl mx-auto">
      <Link to="/advisor/jobs" className="text-secondary">{`← ${t('common.back')}`}</Link>
      <h1 data-page-title tabIndex={-1} className="mt-2">
        {t('job.askcheck')}: {job.title}
      </h1>
      <p className="text-secondary">{job.employer?.name}</p>
      {err && <ErrorBox>{err}</ErrorBox>}
      {job.conditions.map((c) => (
        <div key={c.key} className="card p-4 mb-3">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div>
              <strong>{t(`cond.${c.key}` as Key)}</strong>
              <div className="text-secondary" style={{ fontSize: '1rem' }}>
                {c.value === 'unknown' ? t('common.unknown')
                  : `${c.value} · ${c.source}`}
              </div>
            </div>
            <div className="flex gap-2">
              <Toggle pressed={c.value === 'yes' && c.source === 'advisor'}
                      onClick={() => check(c, 'yes')}>{t('common.yes')}</Toggle>
              <Toggle pressed={c.value === 'no' && c.source === 'advisor'}
                      onClick={() => check(c, 'no')}>{t('common.no')}</Toggle>
            </div>
          </div>
          <Field label={t('advisor.checknote')} id={`cn-${c.key}`}>
            <input id={`cn-${c.key}`} value={notes[c.key] ?? ''}
                   onChange={(e) => setNotes({ ...notes, [c.key]: e.target.value })} />
          </Field>
        </div>
      ))}
    </div>
  )
}

/** Apply on behalf of a walk-in/phone caller (consent required). */
export function AdvisorApplyFor() {
  const { t } = useI18n()
  const { id } = useParams()
  const [job, setJob] = useState<Job | null>(null)
  const [name, setName] = useState('')
  const [method, setMethod] = useState<'phone' | 'sms' | 'email'>('phone')
  const [value, setValue] = useState('')
  const [answer, setAnswer] = useState('')
  const [consent, setConsent] = useState(false)
  const [err, setErr] = useState('')
  const [done, setDone] = useState(false)

  useEffect(() => {
    api<Job>(`/api/jobs/${id}`).then(setJob).catch(() => {})
  }, [id])

  const submit = async () => {
    try {
      await api('/api/advisor/applications', {
        body: {
          job_id: id, name, contact_method: method,
          contact_value: value, answer, consent,
        },
      })
      setDone(true)
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  if (!job) return <p>{t('common.loading')}</p>
  if (done) {
    return (
      <div className="card p-6 max-w-xl mx-auto text-center">
        <h1 data-page-title tabIndex={-1}>{t('apply.sent')}</h1>
        <Link to="/advisor/jobs" className="btn btn-primary">{t('advisor.jobs')}</Link>
      </div>
    )
  }
  return (
    <div className="max-w-2xl mx-auto">
      <Link to="/advisor/jobs" className="text-secondary">{`← ${t('common.back')}`}</Link>
      <h1 data-page-title tabIndex={-1} className="mt-2">
        {t('advisor.applyfor')}: {job.title}
      </h1>
      {err && <ErrorBox>{err}</ErrorBox>}
      <Section title={t('help.contact')}>
        <Field label={t('auth.name')} id="af-name">
          <input id="af-name" value={name} required
                 onChange={(e) => setName(e.target.value)} />
        </Field>
        <div className="flex gap-2 my-3">
          {(['phone', 'sms', 'email'] as const).map((m) => (
            <Toggle key={m} pressed={method === m} onClick={() => setMethod(m)}>
              {t(`apply.${m}` as Key)}
            </Toggle>
          ))}
        </div>
        <Field label={t('apply.value')} id="af-value">
          <input id="af-value" value={value}
                 onChange={(e) => setValue(e.target.value)} />
        </Field>
      </Section>
      <Section title={t('apply.question')}>
        <p className="font-medium mt-0">{job.apply_question}</p>
        <Field label={t('apply.question')} id="af-answer">
          <textarea id="af-answer" value={answer} required
                    onChange={(e) => setAnswer(e.target.value)} />
        </Field>
      </Section>
      <label className="card p-4 flex items-start gap-3 mb-5" style={{ minHeight: 52 }}>
        <input type="checkbox" checked={consent}
               onChange={(e) => setConsent(e.target.checked)}
               className="mt-1" style={{ width: 22, height: 22 }} />
        <span>{t('help.consent')}</span>
      </label>
      <button type="button" className="btn btn-primary w-full"
              disabled={!consent || !name.trim() || !answer.trim()}
              onClick={submit}>
        {t('common.send')}
      </button>
    </div>
  )
}
