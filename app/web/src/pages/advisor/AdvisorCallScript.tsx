import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { CallScript, Job } from '../../types'
import { ErrorBox, Section } from '../../components/ui'
import { daysAgoText } from '../../lib/format'

/** /advisor/jobs/:id/call — "Prepare a call to the employer" script (§4).
    Works without AI via the deterministic rules script; the response
    carries the employer's contact details for the call. */

// backend field ids -> human labels; never show the raw id
const FIELD_LABEL: Record<string, string> = {
  lifting: 'job.lifting',
  pay_amount: 'job.pay', pay_unit: 'job.pay',
  hours_min: 'emp.form.hoursrange', hours_max: 'emp.form.hoursrange',
}

export default function AdvisorCallScript() {
  const { id } = useParams()
  const { t } = useI18n()
  const fieldLabel = (f: string) => {
    if (f.startsWith('condition.')) {
      const k = `cond.${f.slice(10)}`
      const v = t(k as Parameters<typeof t>[0])
      return v === k ? f.slice(10).replaceAll('_', ' ') : v
    }
    const k = FIELD_LABEL[f]
    return k ? t(k as Parameters<typeof t>[0]) : f.replaceAll('_', ' ')
  }
  const [script, setScript] = useState<CallScript | null>(null)
  const [job, setJob] = useState<Job | null>(null)
  const [err, setErr] = useState('')

  useEffect(() => {
    api<CallScript>('/api/ai/advisor/questions', { body: { job_id: id } })
      .then(setScript)
      .catch((e) => setErr(e instanceof ApiError ? e.message : t('common.error')))
    api<Job>(`/api/jobs/${id}`).then(setJob).catch(() => undefined)
  }, [id, t])

  const emp = script?.employer

  return (
    <div className="max-w-3xl mx-auto">
      <Link to="/advisor/jobs" className="text-secondary">{`← ${t('common.back')}`}</Link>
      <h1 data-page-title tabIndex={-1} className="mt-2">{t('advisor.callscript')}</h1>
      {job && (
        <p className="text-secondary" style={{ fontSize: '1.1rem' }}>
          {job.title} — {job.employer?.name}
        </p>
      )}
      {err && <ErrorBox>{err}</ErrorBox>}

      {emp && (
        <Section title={t('advisor.employercontact')}>
          <p className="m-0 font-medium">{emp.name}</p>
          {emp.contact_name && <p className="m-0">{emp.contact_name}</p>}
          <p className="m-0">{emp.contact_phone}{emp.contact_phone && emp.contact_email ? ' · ' : ''}{emp.contact_email}</p>
        </Section>
      )}

      {job && (
        <p className="text-secondary">
          {job.stale
            ? t('jobs.notconfirmed')
            : daysAgoText(job.confirmed_days_ago, t)}
        </p>
      )}

      {script && (
        <Section title={t('advisor.callscript')}>
          <p className="card p-4 font-medium">{script.opening}</p>
          <ol className="m-0 mt-3 pl-5">
            {script.questions.map((q, i) => (
              <li key={i} className="mb-3">
                <p className="m-0 font-medium">{q.question}</p>
                <p className="m-0 text-secondary">{fieldLabel(q.field)}</p>
              </li>
            ))}
          </ol>
          <button type="button" className="btn btn-secondary mt-3 no-print"
                  onClick={() => window.print()}>
            {t('advisor.printsheet')}
          </button>
        </Section>
      )}
      {!script && !err && <p>{t('common.loading')}</p>}
    </div>
  )
}
