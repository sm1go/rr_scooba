import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../../lib/api'
import { useI18n } from '../../i18n/i18n'
import type { CityContract } from '../../types'
import { Chip, ErrorBox, Section } from '../../components/ui'
import { fmtDate } from '../../lib/format'

const TONE = { done: 'yes', behind: 'no', on_track: 'wait' } as const

export default function AdvisorContracts() {
  const { t } = useI18n()
  const [contracts, setContracts] = useState<CityContract[] | null>(null)
  const [err, setErr] = useState('')
  const [recording, setRecording] = useState<CityContract | null>(null)
  const [hiredOn, setHiredOn] = useState('')
  const [note, setNote] = useState('')

  const load = () =>
    api<{ contracts: CityContract[] }>('/api/advisor/contracts')
      .then((r) => setContracts(r.contracts))
      .catch(() => setErr(t('common.error')))
  useEffect(() => { load() }, []) // eslint-disable-line react-hooks/exhaustive-deps

  const record = async () => {
    if (!recording) return
    try {
      await api(`/api/advisor/contracts/${recording.id}/hires`, {
        body: { hired_on: hiredOn, note },
      })
      setRecording(null); setHiredOn(''); setNote('')
      load()
    } catch {
      setErr(t('common.error'))
    }
  }

  if (!contracts) return <p>{t('common.loading')}</p>
  return (
    <div className="max-w-5xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('contracts.title')}</h1>
      <p className="text-secondary">{t('contracts.intro')}</p>
      {err && <ErrorBox>{err}</ErrorBox>}

      {contracts.map((c) => (
        <Section key={c.id} title={c.title}>
          <div className="flex flex-wrap items-center gap-x-4 gap-y-2">
            <Chip tone={TONE[c.status ?? 'on_track']}>
              {t(`contracts.status.${c.status}` as never)}
            </Chip>
            <span>{t('contracts.due')} {fmtDate(c.due)}</span>
            <span>{t('contracts.hires',
                     { n: c.hires_done, req: c.hires_required })}</span>
            <span className="text-secondary">
              {t('contracts.openjobs', { n: c.open_jobs ?? 0 })}
            </span>
          </div>
          <div className="mt-2 rounded overflow-hidden"
               style={{ background: 'var(--color-hairline)', height: 12 }}
               role="img"
               aria-label={t('contracts.hires',
                             { n: c.hires_done, req: c.hires_required })}>
            <div style={{
              width: `${Math.min(100, (c.hires_done / Math.max(1, c.hires_required)) * 100)}%`,
              height: '100%', background: 'var(--color-yes)',
            }} />
          </div>
          <p className="mt-2 mb-0">
            {c.employer?.name} · {c.employer?.contact_name} ·{' '}
            <a href={`tel:${c.employer?.contact_phone}`}>
              {c.employer?.contact_phone}
            </a>
          </p>
          <div className="flex flex-wrap gap-2 mt-3">
            <a className="btn btn-secondary"
               href={`tel:${c.employer?.contact_phone}`}>
              {t('contracts.call')}
            </a>
            <Link className="btn btn-secondary"
                  to={`/advisor/jobs/new?employer=${c.employer?.id}&contract=${c.id}`}>
              {t('contracts.addjob')}
            </Link>
            <Link className="btn btn-secondary"
                  to={`/advisor/jobs?city_contract=1`}>
              {t('contracts.viewjobs')}
            </Link>
            <button type="button" className="btn btn-primary"
                    onClick={() => { setRecording(c)
                                     setHiredOn(new Date().toISOString().slice(0, 10)) }}>
              {t('contracts.recordhire')}
            </button>
          </div>
        </Section>
      ))}

      {recording && (
        <div className="fixed inset-0 flex items-center justify-center p-4"
             style={{ background: 'rgba(0,0,0,.4)', zIndex: 50 }}
             role="dialog" aria-modal="true"
             aria-label={t('contracts.recordhire')}>
          <div className="card p-5 w-full max-w-md">
            <h2 className="m-0 mb-3 font-display" style={{ fontSize: '1.2rem' }}>
              {t('contracts.recordhire')} — {recording.title}
            </h2>
            <label className="block mb-3">
              <span className="font-medium">{t('contracts.hireddate')}</span>
              <input type="date" className="block w-full mt-1" value={hiredOn}
                     onChange={(e) => setHiredOn(e.target.value)} />
            </label>
            <label className="block mb-3">
              <span className="font-medium">{t('contracts.note')}</span>
              <input className="block w-full mt-1" value={note}
                     onChange={(e) => setNote(e.target.value)} />
              <span className="text-secondary">{t('contracts.noname')}</span>
            </label>
            <div className="flex gap-2">
              <button type="button" className="btn btn-secondary flex-1"
                      onClick={() => setRecording(null)}>
                {t('common.cancel')}
              </button>
              <button type="button" className="btn btn-primary flex-1"
                      disabled={!hiredOn} onClick={record}>
                {t('common.save')}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
