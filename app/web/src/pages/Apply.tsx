import { useEffect, useRef, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api, ApiError } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import type { Application, Job, Profile } from '../types'
import { ErrorBox, ErrorState, Field, Section, Toggle } from '../components/ui'
import VoiceInput from '../components/VoiceInput'
import { slotsText } from '../lib/format'

type Method = 'phone' | 'sms' | 'email'

export default function Apply() {
  const { id } = useParams()
  const { t } = useI18n()
  const { user, ready } = useAuth()
  const nav = useNavigate()
  const [job, setJob] = useState<Job | null>(null)
  const [loadErr, setLoadErr] = useState<unknown>(null)
  const [profile, setProfile] = useState<Profile | null>(null)
  const [method, setMethod] = useState<Method>('phone')
  const [value, setValue] = useState('')
  const [availability, setAvailability] = useState('')
  const [answer, setAnswer] = useState('')
  const [meetsMust, setMeetsMust] = useState(false)
  const [wantsTryout, setWantsTryout] = useState(false)
  const [contractOk, setContractOk] = useState(false)
  const [shareCreds, setShareCreds] = useState(false)
  const [shareEvents, setShareEvents] = useState(false)
  const [eventCount, setEventCount] = useState(0)
  const [credCount, setCredCount] = useState(0)
  const [cv, setCv] = useState('')
  const [share, setShare] = useState<Set<string>>(new Set())
  const [event, setEvent] = useState(false)
  const [review, setReview] = useState(false)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState('')
  const [done, setDone] = useState<Application | null>(null)
  const [activeCount, setActiveCount] = useState<number | null>(null)
  const reviewRef = useRef<HTMLHeadingElement>(null)
  const first = useRef(true)
  useEffect(() => {
    if (first.current) { first.current = false; return }
    if (review) reviewRef.current?.focus()
    else document.querySelector<HTMLElement>('h1[data-page-title]')?.focus()
  }, [review])

  const loadJob = () => {
    setLoadErr(null)
    api<Job>(`/api/jobs/${id}`).then((j) => { setJob(j)
      api<{ credentials: { id: string }[] }>(`/api/me/credentials`)
        .then((r) => { setCredCount(r.credentials.length)
                       if (j.qualifications.length) setShareCreds(true) })
        .catch(() => undefined)
      api<{ records: unknown[] }>(`/api/me/event-records`)
        .then((r) => setEventCount(r.records.length))
        .catch(() => undefined) }).catch((e) => setLoadErr(e))
  }
  useEffect(loadJob, [id])

  useEffect(() => {
    if (!ready) return
    if (!user) {
      nav(`/sign-in?back=${encodeURIComponent(`/jobs/${id}/apply`)}`, { replace: true })
      return
    }
    api<Profile>('/api/me/profile').then((p) => {
      setProfile(p)
      setMethod(p.contact_method ?? 'phone')
      setValue(p.contact_method === 'email'
        ? (p.email ?? '') : (p.phone ?? p.email ?? ''))
      setAvailability(slotsText(p.availability, t))
    }).catch(() => {})
    api<{ applications: Application[] }>('/api/me/applications')
      .then((r) => setActiveCount(
        r.applications.filter((a) => a.status === 'sent' || a.status === 'interview').length))
      .catch(() => {})
  }, [user, ready, id, nav])

  if (loadErr) {
    return (
      <ErrorState err={loadErr} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={loadJob}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!job) return <p>{t('common.loading')}</p>
  const commits = job.commitments ?? []
  const openHiring = commits.includes('open_hiring')
  if (done) {
    return (
      <div className="card p-6 max-w-xl mx-auto text-center">
        <h1 data-page-title tabIndex={-1}>{t('apply.sent')}</h1>
        <p>{t('apply.sentbody')}</p>
        <Link to="/applications" className="btn btn-primary">
          {t('nav.applications')}
        </Link>
      </div>
    )
  }

  const submit = async () => {
    setBusy(true); setErr('')
    try {
      const app = await api<Application>('/api/applications', {
        body: {
          job_id: job.id, contact_method: method, contact_value: value,
          availability_note: availability, answer,
          cv_text: job.cv_required && !openHiring ? cv : undefined,
          meets_must_haves: meetsMust, wants_tryout: wantsTryout,
          contract_eligible: contractOk, share_credentials: shareCreds,
          share_event_records: shareEvents,
          shared_needs: [...share], meet_at_event: event,
        },
      })
      setDone(app)
    } catch (e) {
      setErr(e instanceof ApiError ? e.message : t('common.error'))
      setReview(false)
    } finally {
      setBusy(false)
    }
  }

  const needs = profile?.needs ?? []

  return (
    <div className="max-w-2xl mx-auto pb-8">
      <Link to={`/jobs/${job.id}`} className="text-secondary">{`← ${t('common.back')}`}</Link>
      <h1 data-page-title tabIndex={-1} className="mt-2">{t('apply.title')}: {job.title}</h1>
      {activeCount != null && (
        <p className="text-secondary">{activeCount} {t('apply.used')}</p>
      )}
      {err && <ErrorBox>{err}</ErrorBox>}

      {!review ? (
        <>
          <Section title={t('apply.reachme')}>
            <div className="flex gap-2 mb-3">
              {(['phone', 'sms', 'email'] as Method[]).map((m) => (
                <Toggle key={m} pressed={method === m} onClick={() => setMethod(m)}>
                  {t(`apply.${m}` as Key)}
                </Toggle>
              ))}
            </div>
            <Field label={t('apply.value')} id="apply-value">
              <input id="apply-value" value={value}
                     onChange={(e) => setValue(e.target.value)} />
            </Field>
          </Section>

          <Section title={t('apply.availability')}>
            <Field label={t('apply.availability')} id="apply-avail">
              <textarea id="apply-avail" value={availability}
                        onChange={(e) => setAvailability(e.target.value)} />
            </Field>
          </Section>

          {openHiring && (
            <div className="card p-4 mb-4" style={{ background: 'var(--color-wait-bg)' }}>
              <p className="m-0 font-medium">{t('apply.openhiring')}</p>
            </div>
          )}
          {commits.includes('guaranteed_talk') && (
            <div className="card p-4 mb-4">
              <label className="flex items-start gap-3 cursor-pointer font-medium">
                <input type="checkbox" checked={meetsMust}
                       onChange={(e) => setMeetsMust(e.target.checked)}
                       style={{ width: 24, height: 24, marginTop: 2 }} />
                <span>{t('apply.meetsmust')}</span>
              </label>
              {job.qualifications.length > 0 && (
                <ul className="m-0 mt-2 ps-5 text-secondary">
                  {job.qualifications.map((q) => <li key={q}>{q}</li>)}
                </ul>
              )}
            </div>
          )}
          {job.city_contract && (
            <div className="card p-4 mb-4">
              <label className="flex items-start gap-3 cursor-pointer font-medium">
                <input type="checkbox" checked={contractOk}
                       onChange={(e) => setContractOk(e.target.checked)}
                       style={{ width: 24, height: 24, marginTop: 2 }} />
                <span>{t('apply.contract')}</span>
              </label>
            </div>
          )}
          {credCount > 0 && (
            <div className="card p-4 mb-4">
              <label className="flex items-start gap-3 cursor-pointer font-medium">
                <input type="checkbox" checked={shareCreds}
                       onChange={(e) => setShareCreds(e.target.checked)}
                       style={{ width: 24, height: 24, marginTop: 2 }} />
                <span>{t('apply.sharecreds', { n: credCount })}</span>
              </label>
            </div>
          )}
          {eventCount > 0 && (
            <div className="card p-4 mb-4">
              <label className="flex items-start gap-3 cursor-pointer font-medium">
                <input type="checkbox" checked={shareEvents}
                       onChange={(e) => setShareEvents(e.target.checked)}
                       style={{ width: 24, height: 24, marginTop: 2 }} />
                <span>{t('apply.shareevents', { n: eventCount })}</span>
              </label>
            </div>
          )}
          {commits.includes('tryout') && (
            <div className="card p-4 mb-4">
              <label className="flex items-start gap-3 cursor-pointer font-medium">
                <input type="checkbox" checked={wantsTryout}
                       onChange={(e) => setWantsTryout(e.target.checked)}
                       style={{ width: 24, height: 24, marginTop: 2 }} />
                <span>{t('apply.tryout')}</span>
              </label>
            </div>
          )}
          {!openHiring && (
          <Section title={t('apply.question')}>
            <p className="font-medium mt-0">{job.apply_question}</p>
            <Field label={t('apply.question')} id="apply-answer">
              <textarea id="apply-answer" value={answer}
                        onChange={(e) => setAnswer(e.target.value)} required />
            </Field>
            <VoiceInput targetId="apply-answer"
                        onText={(txt) => setAnswer((a) => (a ? `${a} ` : '') + txt)} />
          </Section>
          )}

          {job.cv_required && !openHiring && (
            <Section title={t('apply.cv')}>
              <Field label={t('apply.cv')} id="apply-cv">
                <textarea id="apply-cv" value={cv}
                          onChange={(e) => setCv(e.target.value)} required />
              </Field>
              <VoiceInput targetId="apply-cv"
                          onText={(txt) => setCv((a) => (a ? `${a} ` : '') + txt)} />
            </Section>
          )}

          {needs.length > 0 && (
            <Section title={t('apply.share')}>
              <p className="text-secondary mt-0">{t('apply.sharehint')}</p>
              <div className="flex flex-wrap gap-2">
                {needs.map((k) => (
                  <Toggle key={k} pressed={share.has(k)}
                          onClick={() => setShare((s) => {
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

          {job.event && (
            <Section title={t('job.atevent')}>
              <Toggle pressed={event} onClick={() => setEvent((v) => !v)}>
                {t('apply.event')}
              </Toggle>
            </Section>
          )}

          <button type="button" className="btn btn-primary w-full"
                  onClick={() => { const ok = openHiring || !!answer.trim()
                                   setErr(ok ? '' : t('apply.question'))
                                   if (ok) setReview(true) }}>
            {openHiring ? t('apply.signup') : t('common.next')}
          </button>
        </>
      ) : (
        <section className="card p-5 mb-5">
          <h2 ref={reviewRef} tabIndex={-1} className="m-0 mb-3">{t('apply.review')}</h2>
          <dl className="m-0">
            <dt className="font-medium mt-2">{t('apply.reachme')}</dt>
            <dd className="m-0">{t(`apply.${method}` as Key)}: {value || '—'}</dd>
            <dt className="font-medium mt-2">{t('apply.availability')}</dt>
            <dd className="m-0">{availability || '—'}</dd>
            {!openHiring && (
              <>
                <dt className="font-medium mt-2">{job.apply_question}</dt>
                <dd className="m-0 whitespace-pre-wrap">{answer}</dd>
              </>
            )}
            {openHiring && <dd className="m-0 mt-2">{t('apply.openhiring')}</dd>}
            {meetsMust && <dd className="m-0 mt-2">{t('apply.meetsmust')}</dd>}
            {wantsTryout && <dd className="m-0 mt-2">{t('apply.tryout')}</dd>}
            {contractOk && <dd className="m-0 mt-2">{t('apply.contract')}</dd>}
            {shareCreds && <dd className="m-0 mt-2">{t('apply.sharecreds', { n: credCount })}</dd>}
            {job.cv_required && !openHiring && (
              <>
                <dt className="font-medium mt-2">{t('apply.cv')}</dt>
                <dd className="m-0 whitespace-pre-wrap">{cv}</dd>
              </>
            )}
            {share.size > 0 && (
              <>
                <dt className="font-medium mt-2">{t('apply.share')}</dt>
                <dd className="m-0">{[...share].map((k) => t(`cond.${k}` as Key)).join(', ')}</dd>
              </>
            )}
            {event && <dd className="m-0 mt-2">{t('apply.event')}</dd>}
          </dl>
          <div className="flex gap-2 mt-5">
            <button type="button" className="btn btn-secondary flex-1"
                    onClick={() => setReview(false)}>{t('common.back')}</button>
            <button type="button" className="btn btn-primary flex-1"
                    disabled={busy} onClick={submit}>
              {openHiring ? t('apply.signup') : t('common.send')}
            </button>
          </div>
        </section>
      )}
    </div>
  )
}
