import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowLeft, MessageCircleQuestion } from 'lucide-react'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { BoothData, EventQuestion } from '../types'
import CompanyLogo from '../components/CompanyLogo'
import NeedCardView from '../components/NeedCardView'
import JobRow from '../components/JobRow'

/** Virtual booth (spec §9.7): employer info, need card, open jobs,
 * first-name-only Q&A board. */
export default function BoothPage() {
  const { id, employerId } = useParams()
  const { t } = useI18n()
  const [data, setData] = useState<BoothData | null>(null)
  const [err, setErr] = useState('')
  const [text, setText] = useState('')
  const [ans, setAns] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)

  const load = () => {
    if (!id || !employerId) return
    api<BoothData>(`/api/events/${id}/booths/${employerId}`)
      .then(setData).catch((e) => setErr(e.message))
  }
  useEffect(load, [id, employerId])

  const send = async () => {
    setBusy(true)
    try {
      await api(`/api/events/${id}/booths/${employerId}/questions`,
                { method: 'POST', body: { text } })
      setText(''); load()
    } catch (e) {
      setErr((e as Error).message)
    } finally { setBusy(false) }
  }

  const answer = async (q: EventQuestion) => {
    setBusy(true)
    try {
      await api(`/api/events/${id}/questions/${q.id}/answer`,
                { method: 'POST', body: { answer: ans[q.id] } })
      setAns({ ...ans, [q.id]: '' }); load()
    } catch (e) {
      setErr((e as Error).message)
    } finally { setBusy(false) }
  }

  if (err) return <p className="card p-5" role="alert">{err}</p>
  if (!data) return <p>{t('common.loading')}</p>

  return (
    <div className="grid gap-4">
      <p className="m-0">
        <Link to={`/events/${id}`} className="inline-flex items-center gap-1">
          <ArrowLeft size={16} aria-hidden="true" /> {t('booth.back')}
        </Link>
      </p>
      <header className="card p-5 flex gap-3 items-start flex-wrap">
        <CompanyLogo
          employer={{ name: data.name, logo_color: data.logo_color,
                      field: data.field }} size={56} />
        <div className="flex-1" style={{ minWidth: 0 }}>
          <h1 className="m-0" style={{ fontSize: '1.4rem' }}>{data.name}</h1>
          {data.tagline &&
            <p className="m-0 mt-1 text-secondary">{data.tagline}</p>}
        </div>
        {data.booth && <span className="chip">{data.booth}</span>}
      </header>

      {data.need_item?.need && <NeedCardView e={data.need_item} />}

      {data.open_jobs.length > 0 && (
        <section className="card p-5">
          <h2 className="m-0" style={{ fontSize: '1.1rem' }}>
            {t('booth.jobs')} ({data.open_jobs.length})</h2>
          <ul className="m-0 mt-2 p-0 list-none grid gap-2">
            {data.open_jobs.map((j) =>
              <li key={j.id}><JobRow job={j} /></li>)}
          </ul>
        </section>
      )}

      <section className="card p-5" aria-labelledby="qa-h">
        <h2 id="qa-h" className="m-0 flex items-center gap-2"
            style={{ fontSize: '1.1rem' }}>
          <MessageCircleQuestion size={20} aria-hidden="true" />
          {t('booth.qa.title')}</h2>
        {data.questions.length === 0 &&
          <p className="text-secondary">{t('booth.qa.empty')}</p>}
        <ul className="m-0 mt-2 p-0 list-none grid gap-3">
          {data.questions.map((q) => (
            <li key={q.id} className="p-3 rounded"
                style={{ background: 'var(--color-bg-alt, #f6f7f8)' }}>
              <p className="m-0">
                <strong>{q.asked_by}</strong> — {q.text}</p>
              {q.answer ? (
                <p className="m-0 mt-1">
                  <span className="chip yes">
                    {t('booth.qa.answeredby', { name: q.answered_by ?? '' })}
                  </span>{' '}{q.answer}
                </p>
              ) : data.can_answer ? (
                <div className="mt-2 flex gap-2">
                  <input className="input flex-1"
                         aria-label={t('booth.qa.answer')}
                         value={ans[q.id] ?? ''}
                         onChange={(e) =>
                           setAns({ ...ans, [q.id]: e.target.value })} />
                  <button type="button" className="btn btn-primary"
                          disabled={busy || !(ans[q.id] ?? '').trim()}
                          onClick={() => answer(q)}>
                    {t('booth.qa.answer')}</button>
                </div>
              ) : (
                <p className="m-0 mt-1 text-secondary">
                  {t('booth.qa.waiting')}</p>
              )}
            </li>
          ))}
        </ul>
        {data.can_ask && (
          <form className="mt-3 grid gap-2"
                onSubmit={(e) => { e.preventDefault(); send() }}>
            <label className="font-medium" htmlFor="qa-in">
              {t('booth.qa.ask')}</label>
            <textarea id="qa-in" className="input" rows={2} maxLength={300}
                      placeholder={t('booth.qa.placeholder')}
                      value={text}
                      onChange={(e) => setText(e.target.value)} />
            <div className="flex items-center gap-3">
              <button type="submit" className="btn btn-primary"
                      disabled={busy || !text.trim()}>
                {t('booth.qa.send')}</button>
              <span className="text-secondary" style={{ fontSize: '.85rem' }}>
                {t('booth.qa.max')} · {text.length}/300</span>
            </div>
          </form>
        )}
      </section>
    </div>
  )
}
