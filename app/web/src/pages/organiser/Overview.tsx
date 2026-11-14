import { Bot, CheckCircle2, ShieldCheck, UserRound, XCircle } from 'lucide-react'
import { getAudit, getOverview, getTwinReport } from '../../api'
import { when } from '../../format'
import type { OrganiserOverview, TwinReport } from '../../types'
import { Chip, Loading, PageTitle, Panel } from '../../components/ui'
import { useLoad } from '../../useLoad'

function Tile({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-lg border border-line bg-white p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-1 text-2xl font-semibold">{value}</p>
      {hint && <p className="mt-1 text-xs text-muted">{hint}</p>}
    </div>
  )
}

function Tiles({ o }: { o: OrganiserOverview }) {
  return (
    <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3">
      <li><Tile label="Cards approved" value={String(o.cards_approved)} /></li>
      <li><Tile label="Sparks sent" value={String(o.sparks_sent)} /></li>
      <li><Tile label="Sparks answered" value={`${o.sparks_answered_pct} %`} /></li>
      <li><Tile label="Meetings booked" value={String(o.meetings)} /></li>
      <li><Tile label="Closed within 72 h" value={`${o.closures_within_72h_pct} %`} /></li>
      <li><Tile label="Talents without a meeting" value={o.talents_without_meeting_band} hint="Shown as a range" /></li>
      <li><Tile label="Company time, average" value={`${o.avg_company_minutes} min`} hint="Target: 45 minutes or less" /></li>
    </ul>
  )
}

function TrustLab({ r }: { r: TwinReport }) {
  return (
    <Panel>
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 className="flex items-center gap-2 text-lg">
          <ShieldCheck aria-hidden className="h-5 w-5 text-nordic" /> Trust lab
        </h2>
        {r.placeholder ? (
          <Chip tone="neutral">Not run yet</Chip>
        ) : r.passed ? (
          <Chip tone="green"><CheckCircle2 aria-hidden className="h-3.5 w-3.5" /> Passed</Chip>
        ) : (
          <Chip tone="red"><XCircle aria-hidden className="h-3.5 w-3.5" /> Failed</Chip>
        )}
      </div>
      <p className="mt-2 text-sm text-muted">
        {r.placeholder
          ? 'This panel is ready for the synthetic twin test. The test has not run yet.'
          : `${r.pairs.toLocaleString('en-GB')} pairs of synthetic twins across ${r.runs} ${r.runs === 1 ? 'run' : 'runs'}. A “flip” means the assistant found different claims for the two twins. Allowed: up to ${r.threshold_pct} %.`}
      </p>
      {r.placeholder ? (
        <p className="mt-4 rounded-lg border border-line bg-snow p-4 text-sm">
          This is a demo placeholder, not a fairness result. Run the synthetic
          twin test before drawing conclusions.
        </p>
      ) : (
      <table className="mt-4 w-full text-left text-sm">
        <caption className="sr-only">Flip rate per variant</caption>
        <thead>
          <tr className="border-b border-line">
            <th scope="col" className="py-2 font-semibold">Variant</th>
            <th scope="col" className="py-2 text-right font-semibold">Pairs</th>
            <th scope="col" className="py-2 text-right font-semibold">Flip rate</th>
            <th scope="col" className="py-2 text-right font-semibold">Result</th>
          </tr>
        </thead>
        <tbody>
          {r.variants.map((v) => {
            const ok = v.flip_rate_pct <= r.threshold_pct
            return (
              <tr key={v.name} className="border-b border-line last:border-0">
                <th scope="row" className="py-2 font-normal">{v.name}</th>
                <td className="py-2 text-right">{v.n}</td>
                <td className="py-2 text-right">{v.flip_rate_pct.toFixed(1)} %</td>
                <td className={`py-2 text-right font-medium ${ok ? 'text-moss' : 'text-lingon'}`}>{ok ? 'Within limit' : 'Over limit'}</td>
              </tr>
            )
          })}
        </tbody>
      </table>
      )}
      <p className="mt-3 text-xs text-muted">
        {r.generated_at ? `Generated ${when(r.generated_at)} · model: ${r.provider}` : 'No batch run recorded.'}
      </p>
    </Panel>
  )
}

export default function Overview() {
  const overview = useLoad(getOverview)
  const twin = useLoad(getTwinReport)
  const audit = useLoad(getAudit)
  return (
    <div>
      <PageTitle step="City of Espoo · event team" title="Event overview" lead="TalentMatch Espoo · Tech & ICT, 26 November 2026. No scores or rankings of people." />
      {overview.data ? <Tiles o={overview.data} /> : <Loading />}
      <div className="mt-8">{twin.data ? <TrustLab r={twin.data} /> : <Loading />}</div>
      <Panel className="mt-8">
        <h2 className="text-lg">Recent actions</h2>
        <p className="mt-1 text-sm text-muted">Every assistant suggestion and every human approval is logged.</p>
        {!audit.data ? (
          <Loading />
        ) : (
          <ul className="mt-4 flex flex-col divide-y divide-line">
            {audit.data.slice(0, 20).map((a, i) => (
              <li key={i} className="flex gap-3 py-2 text-sm">
                {a.actor === 'ai' ? (
                  <Bot aria-hidden className="mt-0.5 h-4 w-4 shrink-0 text-muted" />
                ) : (
                  <UserRound aria-hidden className="mt-0.5 h-4 w-4 shrink-0 text-nordic" />
                )}
                <div className="min-w-0 flex-1">
                  <p>
                    <Chip tone={a.actor === 'ai' ? 'neutral' : 'blue'}>{a.actor === 'ai' ? 'Assistant' : 'Human'}</Chip>{' '}
                    <span className="font-medium">{a.action}</span> — {a.detail}
                  </p>
                  <p className="text-xs text-muted">{when(a.at)}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </Panel>
    </div>
  )
}
