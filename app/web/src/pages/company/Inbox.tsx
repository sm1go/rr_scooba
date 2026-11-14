import { useState } from 'react'
import { Link } from 'react-router-dom'
import { CalendarClock, Check, Lock } from 'lucide-react'
import { getCompanySparks, respondSpark } from '../../api'
import { COMPANY_ID } from '../../state/company'
import { when } from '../../format'
import type { InboxSpark, Requirement } from '../../types'
import ClaimView from '../../components/ClaimView'
import { Button, Chip, Loading, Note, PageTitle, Panel } from '../../components/ui'
import { useLoad } from '../../useLoad'
import CompanyNav from './nav'

function SparkItem({ spark, requirements, onChange }: { spark: InboxSpark; requirements: Requirement[]; onChange: (s: InboxSpark) => void }) {
  const [choosing, setChoosing] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function respond(decision: 'accept' | 'decline', reason_chip?: string) {
    setBusy(true)
    setError(null)
    try {
      const r = await respondSpark(spark.id, { decision, reason_chip })
      onChange({ ...spark, status: r.status, revealed_name: r.revealed_name, slot: r.slot })
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not update this Spark.')
    } finally {
      setBusy(false)
      setChoosing(false)
    }
  }

  const open = spark.status === 'sent'
  return (
    <li className="rounded-lg border border-line bg-white p-4">
      {error && <Note tone="red" role="alert">{error}</Note>}
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="font-semibold">{spark.revealed_name ?? spark.pseudonym}</p>
        {open ? (
          <p className="inline-flex items-center gap-1 text-sm text-muted">
            <CalendarClock aria-hidden className="h-4 w-4" /> Answer by {when(spark.deadline)}
          </p>
        ) : (
          <Chip tone={spark.status === 'accepted' ? 'green' : 'neutral'}>{spark.status === 'accepted' ? 'Accepted' : 'Not now · Spark returned'}</Chip>
        )}
      </div>
      <div className="mt-3">
        <ClaimView claim={spark.claim} />
      </div>
      {spark.note && <p className="mt-3 rounded bg-snow p-2 text-sm">Note from talent: “{spark.note}”</p>}

      {spark.status === 'accepted' && (
        <div className="mt-3 rounded-lg bg-moss-tint p-3 text-sm">
          <p>
            Meeting slot: <strong>{spark.slot ?? 'to be set'}</strong>
          </p>
          <p className="mt-1 inline-flex items-center gap-1 text-muted">
            <Lock aria-hidden className="h-3.5 w-3.5" /> Revealed after mutual yes
          </p>
        </div>
      )}

      {open && !choosing && (
        <div className="mt-4 flex flex-wrap gap-3">
          <Button disabled={busy} onClick={() => respond('accept')}>
            <Check aria-hidden className="h-4 w-4" /> Accept
          </Button>
          <Button variant="secondary" disabled={busy} onClick={() => setChoosing(true)}>
            Not now
          </Button>
        </div>
      )}
      {open && choosing && (
        <fieldset className="mt-4">
          <legend className="text-sm font-medium">Which must-have was not shown yet? The talent sees this reason.</legend>
          <div className="mt-2 flex flex-wrap gap-2">
            {requirements.map((r) => (
              <Button key={r.id} variant="secondary" disabled={busy} onClick={() => respond('decline', r.id)}>
                {r.text}
              </Button>
            ))}
            <Button variant="quiet" onClick={() => setChoosing(false)}>
              Cancel
            </Button>
          </div>
        </fieldset>
      )}
    </li>
  )
}

export default function Inbox() {
  const { data, setData, error } = useLoad(() => getCompanySparks(COMPANY_ID))
  const requirements = data?.by_requirement.map((g) => g.requirement) ?? []

  function update(s: InboxSpark) {
    if (!data) return
    setData({
      ...data,
      by_requirement: data.by_requirement.map((g) => ({ ...g, sparks: g.sparks.map((x) => (x.id === s.id ? s : x)) })),
    })
  }

  return (
    <div>
      <CompanyNav />
      <PageTitle
        title="Sparks"
        lead="Each Spark pairs one thing a person has done with one of your must-haves. Names stay hidden until you both say yes."
      />
      {error && <Note tone="red">{error}</Note>}
      {!data && !error && <Loading />}
      {data && (
        <>
          <p className="mb-6 text-sm text-muted">About {data.minutes_estimate} minutes to answer all. Unanswered Sparks go back to the talent at the deadline.</p>
          <div className="flex flex-col gap-8">
            {data.by_requirement.map((g) => (
              <Panel key={g.requirement.id}>
                <h2 className="text-lg">{g.requirement.text}</h2>
                <p className="mt-1 text-sm text-muted">How we'll check it: {g.requirement.how_we_check}</p>
                {g.sparks.length === 0 ? (
                  <p className="mt-3 text-muted">No Sparks for this must-have yet.</p>
                ) : (
                  <ul className="mt-4 flex flex-col gap-3">
                    {g.sparks.map((s) => (
                      <SparkItem key={s.id} spark={s} requirements={requirements} onChange={update} />
                    ))}
                  </ul>
                )}
              </Panel>
            ))}
          </div>
          <p className="mt-6">
            <Link to="/company/meetings" className="font-medium text-nordic underline underline-offset-2">
              See your meetings
            </Link>
          </p>
        </>
      )}
    </div>
  )
}
