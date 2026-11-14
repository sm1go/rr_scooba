import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { SupportCatalogue, SupportProgram } from '../types'
import { ErrorState, Section } from '../components/ui'
import ListenButton from '../components/ListenButton'
import { programsFor } from '../lib/support'

export default function SupportPage() {
  const { t } = useI18n()
  const [cat, setCat] = useState<SupportCatalogue | null>(null)
  const [err, setErr] = useState<unknown>(null)
  const [ticks, setTicks] = useState<Set<string>>(new Set())
  const [step, setStep] = useState<1 | 2>(1)

  const load = () => {
    setErr(null)
    api<SupportCatalogue>('/api/support').then(setCat).catch(setErr)
  }
  useEffect(load, [])

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/" backLabel={t('nav.jobs')} />
    )
  }
  if (!cat) return <p>{t('common.loading')}</p>

  const toggle = (id: string) =>
    setTicks((s) => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n })
  const matches = programsFor(ticks, cat.programs)

  return (
    <div className="max-w-3xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('support.title')}</h1>
      <p className="text-secondary">{cat.meta.disclaimer}</p>

      {step === 1 && (
        <Section title={t('support.step1')}>
          <div className="flex flex-col gap-2">
            {cat.situations.map((s) => (
              <label key={s.id} className="card p-4 flex items-center gap-3 cursor-pointer"
                     style={{ minHeight: 52 }}>
                <input type="checkbox" checked={ticks.has(s.id)}
                       onChange={() => toggle(s.id)}
                       style={{ width: 22, height: 22 }} />
                <span>{s.label}</span>
              </label>
            ))}
          </div>
          <button type="button" className="btn btn-primary mt-4"
                  onClick={() => setStep(2)}>
            {t('support.next')}
          </button>
        </Section>
      )}

      {step === 2 && (
        <>
          <button type="button" className="btn btn-quiet mb-3"
                  onClick={() => setStep(1)}>
            {`← ${t('common.back')}`}
          </button>
          <Section title={t('support.step2')}>
            {matches.length === 0 && (
              <p className="text-secondary">{t('support.none')}</p>
            )}
            {matches.map((p) => <ProgramCard key={p.id} p={p} />)}
          </Section>
          <p className="text-secondary mt-2">
            {t('support.checked')}: {cat.meta.checked_on}
          </p>
        </>
      )}
    </div>
  )
}

function ProgramCard({ p }: { p: SupportProgram }) {
  const { t } = useI18n()
  const listen = [p.name, p.amount,
    p.for_resident || p.for_employer || '', t('support.disclaimer')].join('. ')
  return (
    <article className="card p-5 mb-3">
      <h3 className="m-0 font-display" style={{ fontSize: '1.2rem' }}>{p.name}</h3>
      <p className="m-0 mt-1 font-medium">{t('support.amount')}: {p.amount}</p>
      <p className="m-0 mt-1 text-secondary">
        {p.paid_to === 'resident' ? t('support.moneyto.you')
          : p.paid_to === 'employer' ? t('support.moneyto.employer') : '—'}
      </p>
      <p className="m-0 mt-2">{p.for_resident || p.for_employer}</p>
      <p className="m-0 mt-2 text-secondary">
        <a href={p.source_url} target="_blank" rel="noreferrer">
          {t('support.source')}: {p.source_name}
        </a>
      </p>
      <div className="flex gap-2 mt-3 flex-wrap">
        <ListenButton text={listen} />
        <Link to="/help" className="btn btn-secondary">{t('support.ask')}</Link>
      </div>
    </article>
  )
}
