import { useState } from 'react'
import type { ReactNode } from 'react'
import { Check, Send } from 'lucide-react'
import { ApiError, getEvidence, getTalent, getTalentSparks, listCards, sendSpark } from '../../api'
import { TALENT_ID } from '../../state/company'
import { when } from '../../format'
import type { ChallengeCard, Claim, Requirement, Spark } from '../../types'
import ClaimView from '../../components/ClaimView'
import { Button, Chip, Loading, Note, PageTitle, Panel, inputCls } from '../../components/ui'
import { useLoad } from '../../useLoad'
import BudgetDots from './BudgetDots'
import TalentNav from './nav'

const NOTE_MAX = 140

const STATUS: Record<Spark['status'], { label: string; tone: 'neutral' | 'blue' | 'green' }> = {
  sent: { label: 'Waiting for answer', tone: 'blue' },
  accepted: { label: 'Accepted — meeting booked', tone: 'green' },
  declined: { label: 'Not now', tone: 'neutral' },
  refunded: { label: 'Not now · Spark returned', tone: 'neutral' },
}

function Choice({ selected, onClick, children }: { selected: boolean; onClick: () => void; children: ReactNode }) {
  return (
    <button
      type="button"
      aria-pressed={selected}
      onClick={onClick}
      className={`w-full rounded-lg border p-4 text-left ${selected ? 'border-2 border-nordic bg-lake' : 'border-line bg-white hover:border-nordic'}`}
    >
      {children}
    </button>
  )
}

export default function Browse() {
  const cards = useLoad(listCards)
  const talent = useLoad(() => getTalent(TALENT_ID))
  const evidence = useLoad(() => getEvidence(TALENT_ID))
  const sparks = useLoad(() => getTalentSparks(TALENT_ID))
  const [card, setCard] = useState<ChallengeCard | null>(null)
  const [req, setReq] = useState<Requirement | null>(null)
  const [claim, setClaim] = useState<Claim | null>(null)
  const [note, setNote] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<{ tone: 'green' | 'red'; text: string } | null>(null)

  const used = sparks.data ? Math.max(talent.data?.sparks_used ?? 0, sparks.data.filter((s) => s.status === 'sent' || s.status === 'accepted').length) : 0
  const budget = talent.data?.spark_budget ?? 3
  const left = budget - used
  const titleOf = (id: string) => cards.data?.find((c) => c.id === id)?.title ?? id

  function reset() {
    setCard(null)
    setReq(null)
    setClaim(null)
    setNote('')
  }

  async function send() {
    if (!card || !req || !claim) return
    setBusy(true)
    setMsg(null)
    try {
      const s = await sendSpark({ talent_id: TALENT_ID, card_id: card.id, requirement_id: req.id, claim_id: claim.id, note: note.trim() || undefined })
      sparks.setData([s, ...(sparks.data ?? [])])
      setMsg({ tone: 'green', text: `Spark sent to “${card.title}”. They answer by ${when(s.deadline)}.` })
      reset()
    } catch (e) {
      setMsg({ tone: 'red', text: e instanceof ApiError && e.status === 409 ? 'All your Sparks are in use. You get one back if a company says not now.' : 'Could not send the Spark.' })
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <TalentNav />
      <div className="flex flex-wrap items-end justify-between gap-3">
        <PageTitle title="Send a Spark" lead="Pair one thing you have done with one thing a company needs." />
      </div>
      <div className="mb-6">
        <BudgetDots budget={budget} used={used} />
      </div>
      {msg && (
        <div className="mb-4">
          <Note tone={msg.tone} role="status" aria-live="polite">{msg.text}</Note>
        </div>
      )}

      {!cards.data ? (
        <Loading />
      ) : (
        <div className="flex flex-col gap-6">
          <section aria-labelledby="s1">
            <h2 id="s1" className="mb-2 text-lg">1. Choose a challenge</h2>
            <ul className="flex flex-col gap-2">
              {cards.data.map((c) => (
                <li key={c.id}>
                  <Choice selected={card?.id === c.id} onClick={() => { setCard(c); setReq(null); setClaim(null) }}>
                    <span className="block font-semibold">{c.title}</span>
                    <span className="mt-1 block text-sm text-muted">{c.problem_90d}</span>
                    <span className="mt-2 flex flex-wrap gap-2">
                      <Chip>{c.work_mode}</Chip>
                      {c.languages.map((l) => (
                        <Chip key={l.language} tone="blue">
                          {l.language} {l.level} · {l.task} · {l.from_when}
                        </Chip>
                      ))}
                    </span>
                  </Choice>
                </li>
              ))}
            </ul>
          </section>

          {card && (
            <section aria-labelledby="s2">
              <h2 id="s2" className="mb-2 text-lg">2. Which must-have can you show?</h2>
              <ul className="flex flex-col gap-2">
                {card.must_haves.map((r) => (
                  <li key={r.id}>
                    <Choice selected={req?.id === r.id} onClick={() => setReq(r)}>
                      <span className="block font-medium">{r.text}</span>
                      <span className="mt-1 block text-sm text-muted">How they'll check it: {r.how_we_check}</span>
                    </Choice>
                  </li>
                ))}
              </ul>
            </section>
          )}

          {req && (
            <section aria-labelledby="s3">
              <h2 id="s3" className="mb-2 text-lg">3. Choose your proof</h2>
              {evidence.data && evidence.data.claims.length > 0 ? (
                <ul className="flex flex-col gap-2">
                  {evidence.data.claims.map((c) => (
                    <li key={c.id}>
                      <Choice selected={claim?.id === c.id} onClick={() => setClaim(c)}>
                        <ClaimView claim={c} />
                      </Choice>
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted">You have no confirmed claims yet. Tell a work story first.</p>
              )}
            </section>
          )}

          {claim && (
            <Panel>
              <label htmlFor="note" className="font-medium">
                4. A short note (optional)
              </label>
              <textarea
                id="note"
                rows={2}
                maxLength={NOTE_MAX}
                aria-describedby="note-count"
                className={`${inputCls} mt-2`}
                value={note}
                onChange={(e) => setNote(e.target.value.slice(0, NOTE_MAX))}
              />
              <p id="note-count" className="mt-1 text-right text-sm text-muted">
                {note.length} / {NOTE_MAX}
              </p>
              {left <= 0 && (
                <p className="mt-2 text-sm text-muted">
                  All Sparks are in use. You get one back if a company says “Not now” or misses the deadline.
                </p>
              )}
              <Button big className="mt-3 w-full" disabled={busy || left <= 0} onClick={send}>
                <Send aria-hidden className="h-4 w-4" /> {busy ? 'Sending…' : 'Send Spark'}
              </Button>
            </Panel>
          )}
        </div>
      )}

      <section aria-labelledby="mine" className="mt-10">
        <h2 id="mine" className="mb-2 text-lg">My Sparks</h2>
        {!sparks.data ? (
          <Loading />
        ) : sparks.data.length === 0 ? (
          <p className="text-muted">No Sparks sent yet.</p>
        ) : (
          <ul className="flex flex-col gap-2">
            {sparks.data.map((s) => (
              <li key={s.id} className="rounded-lg border border-line bg-white p-4">
                <div className="flex flex-wrap items-center justify-between gap-2">
                  <span className="font-medium">{titleOf(s.card_id)}</span>
                  <Chip tone={STATUS[s.status].tone}>
                    {s.status === 'accepted' && <Check aria-hidden className="h-3 w-3" />}
                    {STATUS[s.status].label}
                  </Chip>
                </div>
                <p className="mt-1 text-sm text-muted">
                  {s.status === 'accepted' && s.slot ? `Meeting: ${s.slot}` : `Answer by ${when(s.deadline)}`}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  )
}
