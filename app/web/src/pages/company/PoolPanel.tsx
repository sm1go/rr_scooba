import { Users } from 'lucide-react'
import type { Pool } from '../../types'
import { Panel } from '../../components/ui'

export default function PoolPanel({ pool, updating }: { pool: Pool | null; updating: boolean }) {
  return (
    <Panel tint>
      <h2 className="flex items-center gap-2 text-lg">
        <Users aria-hidden className="h-5 w-5 text-nordic" /> Pool Proof
      </h2>
      <p className="mt-1 text-sm text-muted">People registered for this event who could match the card today:</p>
      <p className="mt-2 text-3xl font-semibold text-nordic-dark" aria-live="polite">
        {pool ? pool.band : '…'}
        {updating && <span className="ml-2 align-middle text-sm font-normal text-muted">updating…</span>}
      </p>
      {pool && pool.elasticity.length > 0 && (
        <>
          <h3 className="mt-4 text-sm font-semibold">If you drop one must-have</h3>
          <ul className="mt-1 flex flex-col gap-1 text-sm">
            {pool.elasticity.map((e) => (
              <li key={e.requirement_id}>
                without “{e.text}”: <strong>{e.band_without}</strong>
              </li>
            ))}
          </ul>
        </>
      )}
      <p className="mt-4 text-sm text-muted">Counts are shown in ranges to protect privacy. No people are listed.</p>
    </Panel>
  )
}
