import { CheckCircle2 } from 'lucide-react'
import type { TraceStep } from '../../types'

const TOOL_LABELS: Record<string, string> = {
  read_ad: 'Read the ad',
  read_image: 'Read the screenshot',
  esco_search: 'Looked up skills',
  draft_card: 'Drafted the card',
  lint: 'Checked for unfair wording',
  pool_bands: 'Checked the pool size',
  pool: 'Checked the pool size',
}

const label = (tool: string) => TOOL_LABELS[tool] ?? tool.replace(/_/g, ' ').replace(/^\w/, (c) => c.toUpperCase())

export default function Trace({ steps }: { steps: TraceStep[] }) {
  return (
    <ol className="mt-3 flex flex-col gap-2">
      {steps.map((s, i) => (
        <li key={i} className="flex gap-2">
          <CheckCircle2 aria-hidden className="mt-0.5 h-4 w-4 shrink-0 text-moss" />
          <span>
            <span className="font-medium">{label(s.tool)}:</span> {s.output_summary}
          </span>
        </li>
      ))}
    </ol>
  )
}
