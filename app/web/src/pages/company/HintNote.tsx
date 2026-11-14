import { Lightbulb } from 'lucide-react'
import type { LintHint } from '../../types'
import { Button, SuggestedLabel } from '../../components/ui'

export default function HintNote({
  hint,
  onApply,
  actionLabel = 'Use suggestion',
}: {
  hint: LintHint
  onApply: () => void
  actionLabel?: string
}) {
  return (
    <aside className="rounded-lg border border-line border-l-4 border-l-nordic bg-white p-3 text-sm" aria-label={`Note about “${hint.trigger}”`}>
      <p className="flex items-start gap-2 font-medium">
        <Lightbulb aria-hidden className="mt-0.5 h-4 w-4 shrink-0 text-nordic" />
        “{hint.trigger}” may shut out people who can do the job.
      </p>
      <p className="mt-1">{hint.why}</p>
      {hint.law && <p className="mt-1 text-muted">Law: {hint.law}</p>}
      <p className="mt-2">
        Try: <strong>{hint.suggestion}</strong>
      </p>
      <p className="mt-1 text-muted">
        Pool: {hint.pool_before} → {hint.pool_after}
      </p>
      <div className="mt-2 flex flex-wrap items-center justify-between gap-2">
        <SuggestedLabel />
        <Button variant="secondary" onClick={onApply}>
          {actionLabel}
        </Button>
      </div>
    </aside>
  )
}
