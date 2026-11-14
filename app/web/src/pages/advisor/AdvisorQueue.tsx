import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { Key } from '../../i18n/en'
import type { HelpRequest } from '../../types'
import { Chip, ErrorState, Field, Toggle } from '../../components/ui'
import { fmtDate } from '../../lib/format'

const BUCKETS = ['new', 'in_progress', 'done'] as const

export default function AdvisorQueue() {
  const { t, lang } = useI18n()
  const [bucket, setBucket] = useState<(typeof BUCKETS)[number]>('new')
  const [items, setItems] = useState<HelpRequest[] | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const [editing, setEditing] = useState<string | null>(null)
  const [reply, setReply] = useState('')
  const [notes, setNotes] = useState<Record<string, string>>({})
  const [checked, setChecked] = useState<Record<string, 'yes' | 'no'>>({})

  const load = () => {
    setErr(null)
    api<{ help_requests: HelpRequest[] }>(
      `/api/advisor/help-requests?status=${bucket}`)
      .then((r) => setItems(r.help_requests))
      .catch((e) => { setErr(e); setItems([]) })
  }
  useEffect(load, [bucket])

  const update = async (id: string, status: string, advisor_reply = '') => {
    try {
      await api(`/api/advisor/help-requests/${id}`, {
        body: { status, advisor_reply },
      })
      setEditing(null); setReply('')
      load()
    } catch (e) { setErr(e) }
  }

  const check = async (h: HelpRequest, key: string, value: 'yes' | 'no') => {
    if (!h.job) return
    const ck = `${h.id}:${key}`
    try {
      await api(`/api/advisor/jobs/${h.job.id}/conditions`, {
        method: 'PUT',
        body: { key, value, note: notes[ck] ?? '' },
      })
      setChecked((s) => ({ ...s, [ck]: value }))
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  if (err && items !== null) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!items) return <p>{t('common.loading')}</p>
  return (
    <div className="max-w-4xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('advisor.requests')}</h1>
      <div className="flex gap-2 mb-4 flex-wrap">
        {BUCKETS.map((b) => (
          <Toggle key={b} pressed={bucket === b} onClick={() => setBucket(b)}>
            {t(`advisor.status.${b}` as Key)}
          </Toggle>
        ))}
      </div>
      {items.length === 0 && <p>{t('advisor.empty')}</p>}
      {items.map((h) => (
        <article key={h.id} className="card p-5 mb-3">
          <div className="flex justify-between gap-3">
            <div className="min-w-0 flex-1">
              <h2 className="m-0" style={{ fontSize: '1.15rem' }}>
                {t(`help.kind.${h.kind}` as Key)}
              </h2>
              <p className="m-0 mt-1 text-secondary">
                {h.name} · {h.contact_method}: {h.contact_value}
                {' · '}{fmtDate(h.created_at, lang)}
              </p>
              {h.job && (
                <p className="m-0 mt-1">
                  <Link to={`/jobs/${h.job.id}`}>{h.job.title}</Link>
                  <span className="text-secondary"> — {h.job.employer_name}</span>
                </p>
              )}
            </div>
            <Chip tone="wait" style={{ alignSelf: 'flex-start' }}>
              {t(`advisor.status.${h.status}` as Key)}
            </Chip>
          </div>

          {h.job && (h.job.employer_contact_name || h.job.employer_contact_phone) && (
            <p className="m-0 mt-2 text-secondary">
              {t('advisor.employercontact')}: {h.job.employer_contact_name}
              {h.job.employer_contact_phone && ` · ${h.job.employer_contact_phone}`}
              {h.job.employer_contact_email && ` · ${h.job.employer_contact_email}`}
            </p>
          )}

          {h.message && <p className="mt-2 mb-0">{h.message}</p>}

          {h.kind === 'check_conditions' && h.job && h.condition_keys.length > 0 && (
            <div className="mt-3">
              {h.condition_keys.map((k) => {
                const ck = `${h.id}:${k}`
                const done = checked[ck]
                return (
                  <div key={k} className="card p-4 mb-2">
                    <div className="flex flex-wrap items-center justify-between gap-2">
                      <strong>{t(`cond.${k}` as Key)}</strong>
                      {done ? (
                        <Chip tone="yes" style={{ alignSelf: 'flex-start' }}>
                          {done === 'yes' ? t('common.yes') : t('common.no')}
                          {' · '}{t('advisor.checkedbyyou')}
                        </Chip>
                      ) : (
                        <div className="flex gap-2">
                          <button type="button" className="btn btn-secondary"
                                  onClick={() => check(h, k, 'yes')}>
                            {t('common.yes')}
                          </button>
                          <button type="button" className="btn btn-secondary"
                                  onClick={() => check(h, k, 'no')}>
                            {t('common.no')}
                          </button>
                        </div>
                      )}
                    </div>
                    {!done && (
                      <Field label={t('advisor.checknote')} id={`n-${ck}`}>
                        <input id={`n-${ck}`} value={notes[ck] ?? ''}
                               onChange={(e) => setNotes((s) => ({ ...s, [ck]: e.target.value }))} />
                      </Field>
                    )}
                  </div>
                )
              })}
            </div>
          )}
          {h.advisor_reply && (
            <p className="mt-2 mb-0 text-secondary">↩ {h.advisor_reply}</p>
          )}

          {h.status !== 'done' && (
            editing === h.id ? (
              <div className="mt-3 card p-4">
                <Field label={t('advisor.reply')} id={`rep-${h.id}`}>
                  <textarea id={`rep-${h.id}`} value={reply}
                            onChange={(e) => setReply(e.target.value)} />
                </Field>
                <div className="flex gap-2 flex-wrap">
                  <button type="button" className="btn btn-secondary"
                          onClick={() => setEditing(null)}>
                    {t('common.back')}
                  </button>
                  <button type="button" className="btn btn-primary"
                          onClick={() => update(h.id, 'in_progress', reply)}>
                    {t('advisor.take')}
                  </button>
                  <button type="button" className="btn btn-primary"
                          onClick={() => update(h.id, 'done', reply)}>
                    {t('advisor.done')}
                  </button>
                </div>
              </div>
            ) : (
              <div className="flex gap-2 mt-3 flex-wrap">
                {h.status === 'new' && (
                  <button type="button" className="btn btn-secondary"
                          onClick={() => update(h.id, 'in_progress')}>
                    {t('advisor.take')}
                  </button>
                )}
                <button type="button" className="btn btn-secondary"
                        onClick={() => setEditing(h.id)}>
                  {t('advisor.reply')}
                </button>
              </div>
            )
          )}
        </article>
      ))}
    </div>
  )
}
