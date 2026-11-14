import type { ButtonHTMLAttributes, HTMLAttributes, ReactNode } from 'react'
import { useState } from 'react'
import { Info } from 'lucide-react'

type Variant = 'primary' | 'secondary' | 'quiet'

const variants: Record<Variant, string> = {
  primary: 'bg-nordic text-white hover:bg-nordic-dark border border-nordic hover:border-nordic-dark',
  secondary: 'bg-white text-nordic border border-nordic hover:bg-lake',
  quiet: 'bg-transparent text-nordic border border-transparent hover:bg-lake underline-offset-2',
}

export function Button({
  variant = 'primary',
  className = '',
  big = false,
  ...rest
}: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: Variant; big?: boolean }) {
  return (
    <button
      type="button"
      {...rest}
      className={`inline-flex items-center justify-center gap-2 rounded-lg font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50 ${
        big ? 'min-h-12 px-6 text-base' : 'min-h-10 px-4 text-sm'
      } ${variants[variant]} ${className}`}
    />
  )
}

export function Panel({ children, className = '', tint = false }: { children: ReactNode; className?: string; tint?: boolean }) {
  return (
    <section className={`rounded-lg border border-line p-5 sm:p-6 ${tint ? 'bg-lake' : 'bg-white'} ${className}`}>{children}</section>
  )
}

export function PageTitle({ step, title, lead }: { step?: string; title: string; lead?: string }) {
  return (
    <header className="mb-6">
      {step && <p className="mb-1 text-sm font-medium text-muted">{step}</p>}
      <h1 className="text-2xl sm:text-3xl">{title}</h1>
      {lead && <p className="mt-2 max-w-2xl text-muted">{lead}</p>}
    </header>
  )
}

type ChipTone = 'neutral' | 'blue' | 'green' | 'red'
const tones: Record<ChipTone, string> = {
  neutral: 'bg-birch text-ink',
  blue: 'bg-lake text-nordic-dark',
  green: 'bg-moss-tint text-moss',
  red: 'bg-lingon-tint text-lingon',
}

export function Chip({ children, tone = 'neutral' }: { children: ReactNode; tone?: ChipTone }) {
  return <span className={`inline-flex items-center gap-1 rounded px-2 py-0.5 text-xs font-medium ${tones[tone]}`}>{children}</span>
}

/** Required label on every AI output, with a small "Why am I seeing this?" disclosure. */
export function SuggestedLabel({ why }: { why?: string }) {
  const [open, setOpen] = useState(false)
  return (
    <div className="text-sm">
      <span className="font-medium text-muted">Suggested — you decide</span>
      {why && (
        <>
          {' · '}
          <button type="button" className="text-nordic underline underline-offset-2" aria-expanded={open} onClick={() => setOpen(!open)}>
            Why am I seeing this?
          </button>
          {open && <p className="mt-1 text-muted">{why}</p>}
        </>
      )}
    </div>
  )
}

export function Note({
  children,
  tone = 'blue',
  ...rest
}: HTMLAttributes<HTMLDivElement> & { children: ReactNode; tone?: 'blue' | 'green' | 'red' }) {
  const cls = tone === 'green' ? 'bg-moss-tint border-moss' : tone === 'red' ? 'bg-lingon-tint border-lingon' : 'bg-lake border-nordic'
  return (
    <div {...rest} className={`flex gap-2 rounded-lg border-l-4 p-3 text-sm ${cls}`} role={rest.role ?? 'note'}>
      <Info aria-hidden className="mt-0.5 h-4 w-4 shrink-0" />
      <div>{children}</div>
    </div>
  )
}

export function Loading({ label = 'Loading…' }: { label?: string }) {
  return (
    <p className="py-8 text-muted" role="status" aria-live="polite">
      {label}
    </p>
  )
}

export function Field({ label, hint, id, children }: { label: string; hint?: string; id: string; children: ReactNode }) {
  return (
    <div className="flex flex-col gap-1">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      {hint && (
        <p id={`${id}-hint`} className="text-sm text-muted">
          {hint}
        </p>
      )}
      {children}
    </div>
  )
}

export const inputCls =
  'w-full rounded-lg border border-line bg-white px-3 py-2 text-base text-ink placeholder:text-muted focus-visible:border-nordic'
