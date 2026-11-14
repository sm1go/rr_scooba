import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useAuth } from '../lib/auth'
import { useI18n } from '../i18n/i18n'
import type { EventSummary } from '../types'
import { ErrorState, Section } from '../components/ui'
import type { Key } from '../i18n/en'

function fmtDate(iso: string) {
  try {
    return new Date(iso + 'T00:00:00').toLocaleDateString(
      document.documentElement.lang || 'en',
      { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  } catch { return iso }
}

export default function Home() {
  const { t } = useI18n()
  const { user } = useAuth()
  const [events, setEvents] = useState<EventSummary[] | null>(null)
  const [err, setErr] = useState<unknown>(null)

  const load = () => {
    setErr(null)
    api<{ events: EventSummary[] }>('/api/events')
      .then((d) => setEvents(d.events)).catch(setErr)
  }
  useEffect(load, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (err) return <ErrorState err={err} goneLabel={t('ev.gone')} retryLabel={t('err.retry')} onRetry={load} backTo="/" backLabel={t('nav.home')} />
  if (!events) return <p>{t('common.loading')}</p>

  const upcoming = events.filter((e) => e.phase !== 'finished')
  const past = events.filter((e) => e.phase === 'finished')

  const cards: { to: string; title: Key; body: Key }[] = [
    { to: '/jobs', title: 'home.jobs', body: 'home.jobs.sub' },
    { to: '/week', title: 'home.week', body: 'home.week.sub' },
    { to: '/help', title: 'home.advisor', body: 'home.advisor.sub' },
  ]

  return (
    <div className="grid gap-6">
      <div>
        <h1 data-page-title tabIndex={-1}>{t('home.title')}</h1>
        <p className="text-lg max-w-prose">{t('home.sub')}</p>
        <p className="m-0 mt-4 font-display"
           style={{ color: 'var(--color-brand)', fontSize: '1.9rem', lineHeight: 1.2 }}>{t('home.tagline')}</p>
        <p className="m-0 mt-1 text-secondary">{t('home.tagline.sub')}</p>
      </div>

      <Section title={t('home.events')}>
        {upcoming.length === 0 && <p>{t('event.empty')}</p>}
        <ul className="grid gap-3 p-0 list-none">
          {upcoming.map((e) => (
            <li key={e.id}>
              <Link to={`/events/${e.id}`} className="card p-4 grid gap-1 no-underline"
                    style={{ display: 'block', color: 'var(--color-ink)' }}>
                <strong className="text-lg" style={{ color: 'var(--color-brand)' }}>
                  {e.name}
                </strong>
                <span className="block">{fmtDate(e.date)} · {e.venue}</span>
                <span className="block text-secondary">
                  {t(`ev.format.${e.format}` as Key)} · {t(`ev.langname.${e.language}` as Key)}
                </span>
                <span className="block text-secondary">
                  {t(`ev.phase.${e.phase}` as Key)} · {e.employer_count} {t('ev.employers')}
                </span>
                <span className="btn btn-primary mt-2" style={{ display: 'inline-block' }}>
                  {t('ev.see')}
                </span>
              </Link>
            </li>
          ))}
        </ul>
        {past.length > 0 && (
          <details className="mt-3">
            <summary className="cursor-pointer font-medium">{t('ev.past')}</summary>
            <ul className="grid gap-2 p-0 list-none mt-2">
              {past.map((e) => (
                <li key={e.id}>
                  <Link to={`/events/${e.id}`} style={{ color: 'var(--color-brand)' }}>
                    {e.name}
                  </Link>
                  <span className="text-secondary"> · {fmtDate(e.date)}</span>
                </li>
              ))}
            </ul>
          </details>
        )}
      </Section>

      <Section title={t('home.how')}>
        <ol className="m-0 ps-5 grid gap-1">
          <li><strong>{t('ev.tab.before')}</strong> — {t('home.step1')}</li>
          <li><strong>{t('ev.tab.day')}</strong> — {t('home.step2')}</li>
          <li><strong>{t('ev.tab.after')}</strong> — {t('home.step3')}</li>
        </ol>
      </Section>

      <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))' }}>
        {cards.map((c) => (
          <Link key={c.to} to={c.to} className="card p-4 no-underline"
                style={{ color: 'var(--color-ink)', minHeight: 44 }}>
            <strong className="block mb-1" style={{ color: 'var(--color-brand)' }}>
              {t(c.title)}
            </strong>
            <span className="text-secondary">{t(c.body)}</span>
          </Link>
        ))}
        {!user && (
          <Link to="/sign-up" className="card p-4 no-underline"
                style={{ color: 'var(--color-ink)', minHeight: 44 }}>
            <strong className="block mb-1" style={{ color: 'var(--color-brand)' }}>
              {t('home.signup')}
            </strong>
            <span className="text-secondary">{t('home.signup.sub')}</span>
          </Link>
        )}
      </div>
    </div>
  )
}
