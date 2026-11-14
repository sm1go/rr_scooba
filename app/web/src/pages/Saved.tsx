import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../lib/api'
import { useI18n } from '../i18n/i18n'
import type { Job } from '../types'
import JobRow from '../components/JobRow'

export default function Saved() {
  const { t } = useI18n()
  const [jobs, setJobs] = useState<Job[] | null>(null)
  useEffect(() => {
    api<{ jobs: Job[] }>('/api/me/saved').then((r) => setJobs(r.jobs)).catch(() => setJobs([]))
  }, [])
  if (!jobs) return <p>{t('common.loading')}</p>
  return (
    <div className="max-w-3xl mx-auto">
      <h1 data-page-title tabIndex={-1}>{t('saved.title')}</h1>
      {jobs.length === 0 && (
        <div className="card p-6 text-center">
          <p>{t('saved.empty')}</p>
          <Link to="/jobs" className="btn btn-primary">{t('nav.jobs')}</Link>
        </div>
      )}
      {jobs.map((j) => <JobRow key={j.id} job={j} />)}
    </div>
  )
}
