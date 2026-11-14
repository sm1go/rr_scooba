import { Plus, Trash2 } from 'lucide-react'
import { CEFR_LEVELS } from '../../types'
import type { Cefr, LanguageNeed } from '../../types'
import { Button, inputCls } from '../../components/ui'

type Props = { rows: LanguageNeed[]; onChange: (rows: LanguageNeed[]) => void }

export default function LanguageGrid({ rows, onChange }: Props) {
  const set = (i: number, patch: Partial<LanguageNeed>) => onChange(rows.map((r, j) => (j === i ? { ...r, ...patch } : r)))

  return (
    <fieldset>
      <legend className="text-lg font-semibold">Language needs</legend>
      <p className="mt-1 text-sm text-muted">Say what the language is for, which level, and from when.</p>
      <div className="mt-3 flex flex-col gap-3">
        {rows.map((r, i) => (
          <div key={i} className="grid grid-cols-2 gap-2 rounded-lg border border-line p-3 sm:grid-cols-[1fr_5rem_1.5fr_1fr_auto] sm:items-end">
            <label className="flex flex-col gap-1 text-sm">
              Language
              <input className={inputCls} value={r.language} onChange={(e) => set(i, { language: e.target.value })} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              Level
              <select className={inputCls} value={r.level} onChange={(e) => set(i, { level: e.target.value as Cefr })}>
                {CEFR_LEVELS.map((l) => (
                  <option key={l}>{l}</option>
                ))}
              </select>
            </label>
            <label className="col-span-2 flex flex-col gap-1 text-sm sm:col-span-1">
              For which task
              <input className={inputCls} value={r.task} onChange={(e) => set(i, { task: e.target.value })} />
            </label>
            <label className="flex flex-col gap-1 text-sm">
              From when
              <input className={inputCls} value={r.from_when} onChange={(e) => set(i, { from_when: e.target.value })} />
            </label>
            <Button variant="quiet" aria-label={`Remove ${r.language || 'language'}`} onClick={() => onChange(rows.filter((_, j) => j !== i))}>
              <Trash2 aria-hidden className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
      <Button
        variant="quiet"
        className="mt-2"
        onClick={() => onChange([...rows, { language: '', level: 'B1', task: '', from_when: 'from day one' }])}
      >
        <Plus aria-hidden className="h-4 w-4" /> Add a language
      </Button>
    </fieldset>
  )
}
