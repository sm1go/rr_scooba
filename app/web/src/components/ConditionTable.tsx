import type { Condition, Job } from '../types'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'

function fmtDate(iso: string | null): string {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${parseInt(d)}.${parseInt(m)}.${y}`
}

/** Only the facts that are known (yes / no) and who says so; the unknown
    ones are listed once by the caller, not as rows. */
export default function ConditionTable({
  job,
}: { job: Job; jobId?: string }) {
  const { t } = useI18n()
  const known = job.conditions.filter((c) => c.value !== 'unknown')
  if (!known.length && !job.lifting)
    return <p className="m-0">{t('job.noknown')}</p>
  return (
    <div>
      <ul className="list-none p-0 m-0">
        {known.map((c: Condition) => (
          <li key={c.key}
              className="flex flex-wrap items-baseline justify-between gap-2 py-3 border-b"
              style={{ borderColor: 'var(--color-hairline)' }}>
            <span>{t(`cond.${c.key}` as Key)}</span>
            <span className="flex items-center gap-3 text-end">
              {c.value === 'yes' && (
                <span className="chip yes"><span className="dot" aria-hidden="true" />{t('common.yes')}</span>
              )}
              {c.value === 'no' && (
                <span className="chip no"><span className="dot" aria-hidden="true" />{t('common.no')}</span>
              )}
              <span className="text-secondary" style={{ fontSize: '1rem' }}>
                {c.source === 'advisor'
                  ? `${t('job.advisorchecked')} ${fmtDate(c.checked_at)}`
                  : t('job.employersays')}
                {c.note && ` · ${c.note}`}
              </span>
            </span>
          </li>
        ))}
        {job.lifting && (
          <li className="flex flex-wrap items-baseline justify-between gap-2 py-3">
            <span>{t('job.lifting')}</span>
            <span className="chip"><span className="dot" aria-hidden="true" />{job.lifting}</span>
          </li>
        )}
      </ul>
    </div>
  )
}
