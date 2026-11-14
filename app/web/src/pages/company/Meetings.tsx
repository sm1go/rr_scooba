import { Link } from 'react-router-dom'
import { CalendarDays, ChevronRight, Lock } from 'lucide-react'
import { getMeetings } from '../../api'
import { COMPANY_ID } from '../../state/company'
import { Loading, Note, PageTitle } from '../../components/ui'
import { useLoad } from '../../useLoad'
import CompanyNav from './nav'

export default function Meetings() {
  const { data, error } = useLoad(() => getMeetings(COMPANY_ID))
  return (
    <div>
      <CompanyNav />
      <PageTitle title="Meetings on the event day" lead="Each meeting uses the same short sheet: your three must-haves, asked the same way to everyone." />
      {error && <Note tone="red">{error}</Note>}
      {!data && !error && <Loading />}
      {data && data.length === 0 && <p className="text-muted">No meetings yet. Accept a Spark to get one.</p>}
      {data && data.length > 0 && (
        <ul className="flex flex-col gap-3">
          {data.map((m) => (
            <li key={m.id}>
              <Link
                to={`/company/meetings/${m.id}`}
                className="flex items-center justify-between gap-3 rounded-lg border border-line bg-white p-4 text-ink no-underline hover:border-nordic"
              >
                <span>
                  <span className="block font-semibold">{m.talent_name}</span>
                  <span className="mt-1 inline-flex items-center gap-1 text-sm text-muted">
                    <CalendarDays aria-hidden className="h-4 w-4" /> {m.slot}
                  </span>
                  <span className="mt-1 flex items-center gap-1 text-xs text-muted">
                    <Lock aria-hidden className="h-3 w-3" /> Revealed after mutual yes
                  </span>
                </span>
                <span className="inline-flex items-center gap-1 font-medium text-nordic">
                  Open sheet <ChevronRight aria-hidden className="h-4 w-4" />
                </span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
