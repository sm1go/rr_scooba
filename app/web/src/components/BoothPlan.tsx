import { Link } from 'react-router-dom'
import { useI18n } from '../i18n/i18n'
import CompanyLogo from './CompanyLogo'
import { Section } from './ui'

export interface BoothPlanEmployer {
  id: string
  name: string
  booth: string | null
  field?: string
  logo_color?: string
}

/** Self-explanatory booth plan: entrance marker, logo tiles, plan highlight. */
export default function BoothPlan({ employers, inPlan }: {
  employers: BoothPlanEmployer[]
  inPlan?: Set<string>
}) {
  const { t } = useI18n()
  return (
    <Section title={t('booth.title')}>
      <p className="m-0 mb-3 text-secondary">{t('booth.hint')}</p>
      <div className="booth-wrap card p-0">
        <div className="booth-entrance" aria-hidden="true">
          <span className="chip">{t('booth.entrance')}</span>
        </div>
        <div className="booth-grid p-3" role="list">
          {employers.map((e) => {
            const mine = inPlan?.has(e.id)
            return (
              <div key={e.id} role="listitem"
                   className={`booth-cell card p-3${mine ? ' booth-mine' : ''}`}>
                <Link to={`/companies/${e.id}`}
                      className="flex gap-2 items-start stretched-link">
                  <CompanyLogo employer={e} size={36} />
                  <span>
                    <span className="block font-medium">{e.name}</span>
                    {e.booth && (
                      <span className="text-secondary">
                        {t('ev.booth')} {e.booth}</span>
                    )}
                    {mine && (
                      <span className="block font-medium"
                            style={{ color: 'var(--color-brand)' }}>
                        {t('booth.inplan')}</span>
                    )}
                  </span>
                </Link>
              </div>
            )
          })}
        </div>
      </div>
    </Section>
  )
}
