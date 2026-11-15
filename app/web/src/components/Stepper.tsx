import { Check, Lock } from 'lucide-react'
import { useI18n } from '../i18n/i18n'

/** Event-loop stepper (§9.3): ordered list of buttons, done steps ticked,
 * not-yet-usable steps locked with the date they open. */
export default function Stepper({ steps, current, onSelect, doneBefore,
  locked, label }: {
  steps: string[]
  current: number
  onSelect: (i: number) => void
  doneBefore: number      // steps with index < doneBefore show a tick
  locked?: (string | null)[]  // lock label per step, e.g. "Opens 19 Mar"
  label: string
}) {
  const { t } = useI18n()
  return (
    <nav aria-label={label}>
      <ol className="stepper m-0 p-0 list-none">
        {steps.map((s, i) => {
          const done = i < doneBefore
          const active = i === current
          const lock = locked?.[i] ?? null
          return (
            <li key={i}>
              <button type="button"
                      className={`stepper-step${active ? ' active' : ''}` +
                                 (lock ? ' locked' : '')}
                      aria-current={active ? 'step' : undefined}
                      aria-disabled={lock ? true : undefined}
                      disabled={!!lock}
                      onClick={() => onSelect(i)}>
                <span className="stepper-num" aria-hidden="true">
                  {done ? <Check size={14} /> :
                   lock ? <Lock size={13} /> : i + 1}
                </span>
                <span className="stepper-text">
                  <span>{s}</span>
                  {lock &&
                    <span className="stepper-lock">{lock}</span>}
                </span>
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
