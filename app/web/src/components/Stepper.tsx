import { Check } from 'lucide-react'
import { useI18n } from '../i18n/i18n'

/** Event-loop stepper (§8.1): ordered list of buttons, done steps ticked. */
export default function Stepper({ steps, current, onSelect, doneBefore,
  label }: {
  steps: string[]
  current: number
  onSelect: (i: number) => void
  doneBefore: number      // steps with index < doneBefore show a tick
  label: string
}) {
  const { t } = useI18n()
  return (
    <nav aria-label={label}>
      <ol className="stepper m-0 p-0 list-none">
        {steps.map((s, i) => {
          const done = i < doneBefore
          const active = i === current
          return (
            <li key={i}>
              <button type="button"
                      className={`stepper-step${active ? ' active' : ''}`}
                      aria-current={active ? 'step' : undefined}
                      onClick={() => onSelect(i)}>
                <span className="stepper-num" aria-hidden="true">
                  {done ? <Check size={14} /> : i + 1}
                </span>
                <span>{s}</span>
                {done && (
                  <span className="sr-only"> {t('ev.step.done')}</span>)}
              </button>
            </li>
          )
        })}
      </ol>
    </nav>
  )
}
