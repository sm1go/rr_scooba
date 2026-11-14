import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { useI18n } from '../i18n/i18n'
import type { Key } from '../i18n/en'
import { api } from '../lib/api'
import type { Catalog, CompanyProfile } from '../types'
import { districtName } from '../lib/format'
import { Section, ErrorState } from '../components/ui'
import CompanyLogo from '../components/CompanyLogo'
import JobRow from '../components/JobRow'
import JobMap from '../components/JobMap'
import { fmtDate } from '../lib/format'

export default function CompanyProfilePage() {
  const { id } = useParams()
  const { t } = useI18n()
  const [co, setCo] = useState<CompanyProfile | null>(null)
  const [cat, setCat] = useState<Catalog | null>(null)
  const [err, setErr] = useState<unknown>(null)

  useEffect(() => {
    setErr(null)
    api<CompanyProfile>(`/api/companies/${id}`).then(setCo).catch(setErr)
    api<Catalog>('/api/catalog').then(setCat).catch(() => {})
  }, [id])

  if (err) {
    return (
      <ErrorState err={err} gone={t('err.gone')} goneLabel=""
                  retryLabel={t('err.retry')}
                  onRetry={() => api<CompanyProfile>(`/api/companies/${id}`)
                    .then(setCo).catch(setErr)}
                  backTo="/jobs" backLabel={t('nav.jobs')} />
    )
  }
  if (!co) return <p>{t('common.loading')}</p>

  const pinJob = co.jobs.find((j) => j.lat != null && j.lon != null)

  return (
    <div className="grid gap-4">
      <Link to="/jobs" className="text-secondary">{`← ${t('common.back')}`}</Link>
      <div className="flex gap-3 items-start flex-wrap">
        <CompanyLogo employer={co} size={72} />
        <div className="flex-1" style={{ minWidth: 200 }}>
          <h1 data-page-title tabIndex={-1} className="mb-1">{co.name}</h1>
          {co.tagline && <p className="m-0 text-secondary">{co.tagline}</p>}
          <p className="m-0 mt-1 text-secondary">
            {[co.field ? t(`field.${co.field}` as Key) : '',
              co.district && cat ? districtName(co.district, cat.districts)
                : '',
              co.address].filter(Boolean).join(' · ')}
          </p>
        </div>
      </div>

      <dl className="grid gap-2 m-0" style={{
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))' }}>
        <div className="card p-3">
          <dt className="text-secondary">{t('co.size')}</dt>
          <dd className="m-0 font-medium">{co.size_band}</dd>
        </div>
        {!!co.founded && (
          <div className="card p-3">
            <dt className="text-secondary">{t('co.founded')}</dt>
            <dd className="m-0 font-medium">{co.founded}</dd>
          </div>
        )}
        {co.work_languages.length > 0 && (
          <div className="card p-3">
            <dt className="text-secondary">{t('co.langs')}</dt>
            <dd className="m-0 font-medium">{co.work_languages.join(', ')}</dd>
          </div>
        )}
      </dl>

      {pinJob && <JobMap jobs={[pinJob]} height={260} />}

      {co.about && (
        <Section title={t('co.about')}><p className="m-0">{co.about}</p></Section>
      )}
      {co.how_we_welcome && (
        <Section title={t('co.welcome')}><p className="m-0">{co.how_we_welcome}</p></Section>
      )}

      {co.commitments.length > 0 && (
        <Section title={t('co.promises')}>
          <ul className="m-0 ps-5">
            {co.commitments.map((c) => <li key={c}>{t(`commit.${c}` as Key)}</li>)}
          </ul>
        </Section>
      )}

      {co.contracts.length > 0 && (
        <Section title={t('co.contracts')}>
          <ul className="m-0 ps-5">
            {co.contracts.map((c) => <li key={c}>{c}</li>)}
          </ul>
        </Section>
      )}

      {co.badges.length > 0 && (
        <Section title={t('co.badges')}>
          <ul className="grid gap-2 p-0 list-none">
            {co.badges.map((b, i) => (
              <li key={i} className="card p-3">
                {t(`badge.${b.label || b.kind}` as Key,
                   { event: b.event_name })}
              </li>
            ))}
          </ul>
        </Section>
      )}

      {co.events.length > 0 && (
        <Section title={t('co.events')}>
          <div className="grid gap-3">
            {co.events.map((ev) => (
              <div key={ev.event_id} className="card p-4">
                <div className="flex gap-2 flex-wrap items-baseline">
                  <Link to={`/events/${ev.event_id}`} className="font-medium">
                    {ev.name}</Link>
                  <span className="text-secondary">{fmtDate(ev.date)}</span>
                  {ev.past && <span className="chip">{t('ev.past')}</span>}
                  {ev.booth &&
                    <span className="chip">{t('ev.booth')} {ev.booth}</span>}
                </div>
                {ev.need_card && (
                  <div className="mt-2">
                    {ev.need_card.first_week?.length > 0 && (
                      <p className="m-0">
                        <strong>{t('ev.firstweek')}</strong>{' '}
                        {ev.need_card.first_week[0]}
                      </p>
                    )}
                    {ev.need_card.will_teach && (
                      <p className="m-0 text-secondary">
                        <strong>{t('ev.teach')}</strong>{' '}
                        {ev.need_card.will_teach}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Section>
      )}

      {co.jobs.length > 0 && (
        <Section title={t('co.jobs', { n: co.jobs.length })}>
          <ul className="m-0 p-0 list-none grid gap-2">
            {co.jobs.map((j) => <JobRow key={j.id} job={j} />)}
          </ul>
        </Section>
      )}

      {(co.contact_name || co.contact_email || co.contact_phone) && (
        <Section title={t('co.contact')}>
          <p className="m-0">
            {[co.contact_name, co.contact_email, co.contact_phone]
              .filter(Boolean).join(' · ')}
          </p>
        </Section>
      )}
    </div>
  )
}
