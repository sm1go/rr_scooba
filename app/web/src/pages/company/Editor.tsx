import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { CheckCircle2 } from 'lucide-react'
import { approveCard, draftCard, lint, pool as getPool } from '../../api'
import { SAMPLE_AD } from '../../fixtures/company'
import { COMPANY_ID, useDraft } from '../../state/company'
import type { ChallengeCard, LintHint, Pool, Requirement } from '../../types'
import { Button, Field, Note, PageTitle, Panel, SuggestedLabel, inputCls } from '../../components/ui'
import CompanyNav from './nav'
import HintNote from './HintNote'
import LanguageGrid from './LanguageGrid'
import PoolPanel from './PoolPanel'
import NiceToHaves from './NiceToHaves'
import { applyHint, hintKey, locateHint } from './hints'

export default function Editor() {
  const { draft, setDraft } = useDraft()
  const [card, setCard] = useState<ChallengeCard | null>(draft?.card ?? null)
  const [hints, setHints] = useState<LintHint[]>(draft?.lint ?? [])
  const [pool, setPool] = useState<Pool | null>(draft?.pool ?? null)
  const [updating, setUpdating] = useState(false)
  const [approved, setApproved] = useState<ChallengeCard | null>(null)
  const [busy, setBusy] = useState(false)
  const [dismissed, setDismissed] = useState<string[]>([])
  const [error, setError] = useState<string | null>(null)
  const first = useRef(true)

  // Re-check lint and pool after edits (debounced).
  useEffect(() => {
    if (!card) return
    if (first.current) {
      first.current = false
      return
    }
    setUpdating(true)
    const t = setTimeout(async () => {
      try {
        const [l, p] = await Promise.all([lint(card), getPool(card)])
        setHints(l.hints)
        setPool(p)
        setError(null)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Could not refresh the checks.')
      } finally {
        setUpdating(false)
      }
    }, 600)
    return () => clearTimeout(t)
  }, [card])

  if (!card) {
    return (
      <div>
        <CompanyNav />
        <PageTitle title="Your Challenge Card" lead="There is no draft yet. Start by describing your need." />
        <div className="flex flex-wrap gap-3">
          <Link to="/company" className="inline-flex min-h-12 items-center rounded-lg bg-nordic px-6 font-medium text-white hover:bg-nordic-dark">
            Describe your need
          </Link>
          <Button big variant="secondary" onClick={async () => {
              const d = await draftCard({ company_id: COMPANY_ID, text: SAMPLE_AD })
              setDraft(d)
              setCard(d.card)
              setHints(d.lint)
              setPool(d.pool)
            }}>
            Load the sample draft
          </Button>
        </div>
      </div>
    )
  }

  const setReq = (id: string, patch: Partial<Requirement>) =>
    setCard({ ...card, must_haves: card.must_haves.map((r) => (r.id === id ? { ...r, ...patch } : r)) })
  const visible = hints.filter((h) => !dismissed.includes(hintKey(h)))
  const placed = visible.map((h) => ({ h, at: locateHint(card, h) }))
  const notes = (pred: (p: (typeof placed)[number]['at']) => boolean) =>
    placed
      .filter((p) => pred(p.at))
      .map(({ h }) => (
        <HintNote
          key={h.id}
          hint={h}
          actionLabel={JSON.stringify(applyHint(card, h)) === JSON.stringify(card) ? 'Dismiss note' : 'Use suggestion'}
          onApply={() => use(h)}
        />
      ))
  function use(h: LintHint) {
    if (!card) return
    const next = applyHint(card, h)
    if (JSON.stringify(next) === JSON.stringify(card)) setDismissed((d) => [...d, hintKey(h)])
    else setCard(next)
  }

  async function approve() {
    if (!card) return
    setBusy(true)
    setError(null)
    try {
      setApproved(await approveCard(card))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not approve this card.')
    } finally {
      setBusy(false)
    }
  }

  if (approved) {
    return (
      <div>
        <CompanyNav />
        <Panel>
          <p className="flex items-center gap-2 text-xl font-semibold text-moss">
            <CheckCircle2 aria-hidden className="h-6 w-6" /> Card approved
          </p>
          <p className="mt-2">“{approved.title}” is now visible to talent registered for the event. You will get Sparks paired with your must-haves.</p>
          <p className="mt-1 text-muted">The intake is designed to take 45 minutes or less.</p>
          <Link to="/company/sparks" className="mt-4 inline-flex min-h-12 items-center rounded-lg bg-nordic px-6 font-medium text-white hover:bg-nordic-dark">
            Go to Sparks
          </Link>
        </Panel>
      </div>
    )
  }

  return (
    <div>
      <CompanyNav />
      <PageTitle title="Check your Challenge Card" lead="Edit anything. Notes on the right are suggestions — they never block you." />
      {error && <Note tone="red" role="alert">{error}</Note>}
      <SuggestedLabel why="The assistant drafted this card from your ad. Pool counts come from confirmed claims of people who agreed to be counted." />

      <div className="mt-4 grid gap-6 lg:grid-cols-[1fr_300px]">
        <div className="flex flex-col gap-6">
          <Panel>
            <div className="flex flex-col gap-4">
              <Field id="title" label="Card title">
                <input id="title" className={inputCls} value={card.title} onChange={(e) => setCard({ ...card, title: e.target.value })} />
              </Field>
              <Field id="problem" label="The problem to solve in 90 days">
                <textarea id="problem" rows={3} className={inputCls} value={card.problem_90d} onChange={(e) => setCard({ ...card, problem_90d: e.target.value })} />
              </Field>
              <Field id="mode" label="Work mode">
                <input id="mode" className={inputCls} value={card.work_mode} onChange={(e) => setCard({ ...card, work_mode: e.target.value })} />
              </Field>
              {notes((p) => p.kind === 'card')}
            </div>
          </Panel>

          <Panel>
            <h2 className="text-lg">Three must-haves</h2>
            <p className="mt-1 text-sm text-muted">Every candidate is checked the same way.</p>
            <ol className="mt-4 flex flex-col gap-5">
              {card.must_haves.map((r, i) => {
                return (
                  <li key={r.id} className="grid gap-3 md:grid-cols-[1fr_minmax(0,16rem)]">
                    <div className="flex flex-col gap-2">
                      <Field id={`req-${r.id}`} label={`Must-have ${i + 1}`}>
                        <input id={`req-${r.id}`} className={inputCls} value={r.text} onChange={(e) => setReq(r.id, { text: e.target.value })} />
                      </Field>
                      <Field id={`chk-${r.id}`} label="How we'll check it">
                        <input id={`chk-${r.id}`} className={inputCls} value={r.how_we_check} onChange={(e) => setReq(r.id, { how_we_check: e.target.value })} />
                      </Field>
                      {r.esco_label && <p className="text-xs text-muted">Skill (ESCO): {r.esco_label}</p>}
                    </div>
                    <div className="flex flex-col gap-2">
                      {notes((p) => p.kind === 'req' && p.id === r.id)}
                    </div>
                  </li>
                )
              })}
            </ol>
          </Panel>

          <Panel>
            <LanguageGrid rows={card.languages} onChange={(languages) => setCard({ ...card, languages })} />
            <div className="mt-3 flex flex-col gap-2">{notes((p) => p.kind === 'lang')}</div>
          </Panel>

          <Panel>
            <NiceToHaves
              items={card.nice_to_haves}
              onChange={(nice_to_haves) => setCard({ ...card, nice_to_haves })}
              notesFor={(i) => notes((p) => p.kind === 'nice' && p.index === i)}
            />
          </Panel>
        </div>

        <div className="flex flex-col gap-4 lg:sticky lg:top-4 lg:self-start">
          <PoolPanel pool={pool} updating={updating} />
          {visible.length === 0 && !updating && <Note tone="green">No wording notes. The card is ready to approve.</Note>}
          <Button big disabled={busy} onClick={approve}>
            {busy ? 'Approving…' : 'Approve card'}
          </Button>
        </div>
      </div>
    </div>
  )
}
