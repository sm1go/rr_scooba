import { Plus, Trash2 } from 'lucide-react'
import type { ReactNode } from 'react'
import { Button, inputCls } from '../../components/ui'

type Props = { items: string[]; onChange: (items: string[]) => void; notesFor: (index: number) => ReactNode }

export default function NiceToHaves({ items, onChange, notesFor }: Props) {
  return (
    <fieldset>
      <legend className="text-lg font-semibold">Nice to have</legend>
      <p className="mt-1 text-sm text-muted">Not required. Nobody is turned away for missing these.</p>
      <ul className="mt-3 flex flex-col gap-3">
        {items.map((n, i) => (
          <li key={i} className="grid gap-2 md:grid-cols-[1fr_minmax(0,16rem)]">
            <div className="flex items-center gap-2">
              <input aria-label={`Nice to have ${i + 1}`} className={inputCls} value={n} onChange={(e) => onChange(items.map((x, j) => (j === i ? e.target.value : x)))} />
              <Button variant="quiet" aria-label={`Remove “${n}”`} onClick={() => onChange(items.filter((_, j) => j !== i))}>
                <Trash2 aria-hidden className="h-4 w-4" />
              </Button>
            </div>
            <div className="flex flex-col gap-2">{notesFor(i)}</div>
          </li>
        ))}
      </ul>
      <Button variant="quiet" className="mt-2" onClick={() => onChange([...items, ''])}>
        <Plus aria-hidden className="h-4 w-4" /> Add a nice-to-have
      </Button>
    </fieldset>
  )
}
