import { useEffect, useState } from 'react'
import { api } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { SupportCatalogue } from '../../types'
import { ErrorState, Section } from '../../components/ui'

/** /advisor/support — the full support catalogue as a reference table. */
export default function AdvisorSupport() {
  const { t } = useI18n()
  const [cat, setCat] = useState<SupportCatalogue | null>(null)
  const [err, setErr] = useState<unknown>(null)

  const load = () => {
    setErr(null)
    api<SupportCatalogue>('/api/support').then(setCat).catch(setErr)
  }
  useEffect(load, [])

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')} onRetry={load}
                  backTo="/advisor" backLabel={t('nav.requests')} />
    )
  }
  if (!cat) return <p>{t('common.loading')}</p>

  return (
    <div className="max-w-5xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('advisor.support')}</h1>
      <p className="text-secondary mt-2">
        {t('support.checked')}: {cat.meta.checked_on} — {cat.meta.disclaimer}
      </p>
      <Section title={t('support.title')}>
        <div className="overflow-x-auto">
          <table className="w-full" style={{ borderCollapse: 'collapse' }}>
            <thead>
              <tr className="text-left border-b" style={{ borderColor: 'var(--color-ink)' }}>
                <th className="py-2 pe-3" style={{ width: '55%' }}>{t('support.title')}</th>
                <th className="py-2 pe-3">{t('support.amount')}</th>
                <th className="py-2 pe-3">{t('empevent.person')}</th>
                <th className="py-2 pe-3">{t('support.source')}</th>
              </tr>
            </thead>
            <tbody>
              {cat.programs.map((p) => (
                <tr key={p.id} className="border-b align-top"
                    style={{ borderColor: 'var(--color-hairline)' }}>
                  <td className="py-3 pe-3">
                    <strong>{p.name}</strong>
                    <p className="m-0 text-secondary">{p.for_resident || p.for_employer}</p>
                  </td>
                  <td className="py-3 pe-3">{p.amount}</td>
                  <td className="py-3 pe-3">
                    {p.paid_to === 'resident' ? t('support.moneyto.you')
                      : p.paid_to === 'employer' ? t('support.moneyto.employer') : '—'}
                  </td>
                  <td className="py-3 pe-3">
                    <a href={p.source_url} target="_blank" rel="noreferrer">{p.source_name}</a>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Section>
      <Section title={t('support.step1')}>
        <ul className="pl-5 m-0">
          {cat.situations.map((s) => <li key={s.id} className="mb-1">{s.label}</li>)}
        </ul>
      </Section>
    </div>
  )
}
