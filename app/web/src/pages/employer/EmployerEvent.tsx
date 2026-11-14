import { useEffect, useState } from 'react'
import { api, ApiError } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { EmployerEvent, EventTalk } from '../../types'
import { Chip, ErrorBox, ErrorState, Section } from '../../components/ui'

/** /employer/event — the employer's booth view: visitor count, record
    conversations by number, answer each with next step / not now. */
export default function EmployerEventPage() {
  const { t } = useI18n()
  const [ev, setEv] = useState<EmployerEvent | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const [msg, setMsg] = useState('')
  const [code, setCode] = useState('')
  const [busy, setBusy] = useState(false)
  const [answers, setAnswers] = useState<Record<string, { outcome: string; note: string }>>({})

  const load = () => {
    setErr(null)
    api<EmployerEvent>('/api/employer/event').then(setEv).catch(setErr)
  }
  useEffect(load, [])

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/employer" backLabel={t('nav.myjobs')} />
    )
  }
  if (!ev) return <p>{t('common.loading')}</p>
  if (!ev.event) return <p className="card p-5">{t('event.empty')}</p>

  const record = async () => {
    setBusy(true); setMsg('')
    try {
      await api(`/api/employer/event/talks`, { body: { code } })
      setCode('')
      load()
    } catch (e) {
      setMsg(e instanceof ApiError ? e.message : t('common.error'))
    } finally { setBusy(false) }
  }

  const answer = async (talk: EventTalk) => {
    const a = answers[talk.id]
    if (!a?.outcome || !a.note.trim()) return
    try {
      await api(`/api/employer/event/talks/${talk.id}/answer`, {
        body: { outcome: a.outcome, employer_note: a.note.trim() },
      })
      load()
    } catch (e) {
      setMsg(e instanceof ApiError ? e.message : t('common.error'))
    }
  }

  return (
    <div className="max-w-3xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('empevent.title')}</h1>
      <p className="text-secondary" style={{ fontSize: '1.1rem' }}>
        {ev.event.name} · {ev.event.date} · {ev.event.venue}
      </p>
      <div className="grid gap-3 md:grid-cols-2 mb-5">
        <div className="card p-4 text-center">
          <div className="font-display" style={{ fontSize: '2rem' }}>{ev.booth ?? '—'}</div>
          <div className="text-secondary">{t('empevent.booth')}</div>
        </div>
        <div className="card p-4 text-center">
          <div className="font-display" style={{ fontSize: '2rem' }}>{ev.visitors_planned}</div>
          <div className="text-secondary">{t('empevent.planned')}</div>
        </div>
      </div>

      <Section title={t('empevent.record')}>
        {msg && <ErrorBox>{msg}</ErrorBox>}
        <div className="flex gap-2 items-end flex-wrap">
          <label className="flex-1" style={{ minWidth: 200 }}>
            <span className="font-medium block mb-1">{t('empevent.code')}</span>
            <input value={code} inputMode="numeric" maxLength={4}
                   onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                   style={{ fontSize: '1.6rem', letterSpacing: '0.3em', textAlign: 'center' }} />
          </label>
          <button type="button" className="btn btn-primary" disabled={busy || code.length !== 4}
                  onClick={record}>
            {t('empevent.record')}
          </button>
        </div>
      </Section>

      <Section title={t('empevent.talks')}>
        {ev.talks.length === 0 && <p className="text-secondary">{t('empevent.none')}</p>}
        {ev.talks.map((tk) => (
          <article key={tk.id} className="card p-4 mb-3">
            <div className="flex justify-between gap-3 flex-wrap">
              <div>
                <p className="m-0 font-medium">{tk.person_name}</p>
                <p className="m-0 text-secondary">
                  {tk.person_contact_method}: {tk.person_contact_value}
                </p>
              </div>
              <Chip tone={tk.status === 'answered' ? 'yes' : 'wait'}>
                {tk.status === 'answered' ? t('empevent.answered') : t('empevent.needsanswer')}
              </Chip>
            </div>
            {tk.status === 'talked' ? (
              <div className="mt-3">
                <div className="flex gap-2 mb-2">
                  {(['next_step', 'not_now'] as const).map((o) => (
                    <button key={o} type="button"
                            className={`btn ${answers[tk.id]?.outcome === o ? 'btn-primary' : 'btn-quiet'}`}
                            aria-pressed={answers[tk.id]?.outcome === o}
                            onClick={() => setAnswers({
                              ...answers, [tk.id]: { outcome: o, note: answers[tk.id]?.note ?? '' },
                            })}>
                      {o === 'next_step' ? t('empevent.nextstep') : t('empevent.notnow')}
                    </button>
                  ))}
                </div>
                <label className="block">
                  <span className="font-medium block mb-1">{t('empevent.note')}</span>
                  <input value={answers[tk.id]?.note ?? ''}
                         onChange={(e) => setAnswers({
                           ...answers,
                           [tk.id]: { outcome: answers[tk.id]?.outcome ?? '', note: e.target.value },
                         })} />
                </label>
                <button type="button" className="btn btn-secondary mt-2"
                        disabled={!answers[tk.id]?.outcome || !answers[tk.id]?.note?.trim()}
                        onClick={() => answer(tk)}>
                  {t('empevent.send')}
                </button>
              </div>
            ) : (
              <p className="m-0 mt-2 text-secondary">
                {tk.outcome === 'next_step' ? t('empevent.nextstep') : t('empevent.notnow')}
                {' — '}{tk.employer_note}
              </p>
            )}
          </article>
        ))}
      </Section>
    </div>
  )
}
