import type { Condition, Job } from '../types'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import { Link } from 'react-router-dom'

function fmtDate(iso: string | null): string {
  if (!iso) return ''
  const [y, m, d] = iso.split('-')
  return `${parseInt(d)}.${parseInt(m)}.${y}`
}

/** The 10 conditions + lifting: three clearly different states. */
export default function ConditionTable({
  job, jobId,
}: { job: Job; jobId: string }) {
  const { t } = useI18n()
  return (
    <div>
      <ul className="list-none p-0 m-0">
        {job.conditions.map((c: Condition) => (
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
              {c.value === 'unknown' && (
                <span className="chip wait"><span className="dot" aria-hidden="true" />{t('common.unknown')}</span>
              )}
              <span className="text-secondary" style={{ fontSize: '1rem' }}>
                {c.value !== 'unknown' && (
                  c.source === 'advisor'
                    ? `${t('job.advisorchecked')} ${fmtDate(c.checked_at)}`
                    : t('job.employersays')
                )}
                {c.note && ` · ${c.note}`}
                {c.value === 'unknown' && (
                  <>
                    {' '}
                    <Link to={`/help?job=${jobId}&keys=${c.key}`}>
                      {t('job.askcheck')}
                    </Link>
                  </>
                )}
              </span>
            </span>
          </li>
        ))}
        <li className="flex flex-wrap items-baseline justify-between gap-2 py-3">
          <span>{t('job.lifting')}</span>
          <span>
            {job.lifting
              ? <span className="chip"><span className="dot" aria-hidden="true" />{job.lifting}</span>
              : <span className="chip wait"><span className="dot" aria-hidden="true" />{t('common.unknown')}</span>}
          </span>
        </li>
      </ul>
    </div>
  )
}
