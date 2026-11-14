import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { ApiError } from '../lib/api'
import { useI18n } from '../i18n/i18n'

export function Chip({
  children, tone, title, style,
}: {
  children: ReactNode; tone?: 'yes' | 'wait' | 'no'; title?: string
  style?: React.CSSProperties
}) {
  return (
    <span className={`chip ${tone ?? ''}`} title={title} style={style}>
      <span className="dot" aria-hidden="true" />
      {children}
    </span>
  )
}

export function Field({
  label, children, hint, id,
}: { label: string; children: ReactNode; hint?: string; id?: string }) {
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {children}
      {hint && <p className="text-secondary mt-1" style={{ fontSize: '1rem' }}>{hint}</p>}
    </div>
  )
}

export function Section({
  title, children, action,
}: { title: string; children: ReactNode; action?: ReactNode }) {
  return (
    <section className="card p-5 mb-5">
      <div className="flex items-start justify-between gap-3 mb-3">
        <h2 className="m-0">{title}</h2>
        {action}
      </div>
      {children}
    </section>
  )
}

export function Toggle({
  pressed, onClick, children, className = '',
}: {
  pressed: boolean; onClick: () => void; children: ReactNode
  className?: string
}) {
  return (
    <button
      type="button"
      aria-pressed={pressed}
      onClick={onClick}
      className={`btn ${pressed ? 'btn-primary' : 'btn-quiet'} ${className}`}
      style={{ minHeight: 48 }}
    >
      {children}
    </button>
  )
}

export function ErrorBox({ children }: { children: ReactNode }) {
  return (
    <div role="alert" className="card p-4 mb-4"
         style={{ borderColor: 'var(--color-no)', background: 'var(--color-no-bg)' }}>
      {children}
    </div>
  )
}

/** Full-page error: specific message for offline / gone / generic,
    always with a way forward. */
export function ErrorState({
  err, gone, goneLabel, retryLabel, onRetry, backTo, backLabel,
}: {
  err: unknown
  gone?: string
  goneLabel: string
  retryLabel: string
  onRetry?: () => void
  backTo: string
  backLabel: string
}) {
  const { t } = useI18n()
  const status = err instanceof ApiError ? err.status : null
  const msg = status === 404 ? gone
    : status === 0 ? t('err.offline')
    : t('common.error')
  void goneLabel
  return (
    <div className="card p-6 max-w-xl mx-auto text-center" role="alert">
      <p className="font-medium mt-0">{msg}</p>
      <div className="flex gap-2 justify-center flex-wrap">
        {status === 0 && onRetry && (
          <button type="button" className="btn btn-primary" onClick={onRetry}>
            {retryLabel}
          </button>
        )}
        <Link to={backTo} className="btn btn-secondary">{backLabel}</Link>
      </div>
    </div>
  )
}

/** Inline help offer inside a job list — quiet card, not floating. */
export function HelpCard() {
  const { t } = useI18n()
  return (
    <div className="card p-5 mb-3 flex flex-wrap items-center justify-between gap-3">
      <p className="m-0">{t('jobs.helpcard')}</p>
      <Link to="/help" className="btn btn-secondary">{t('jobs.askadvisor')}</Link>
    </div>
  )
}
