import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { ArrowRight, Check, LifeBuoy } from 'lucide-react'
import { closeMeeting, getSheet } from '../../api'
import type { ClosureRequest, ClosureResponse } from '../../types'
import { Button, Loading, Note, PageTitle, Panel, inputCls } from '../../components/ui'
import { useLoad } from '../../useLoad'
import CompanyNav from './nav'

type Outcome = ClosureRequest['outcome']

export default function Closure() {
  const { id = '' } = useParams()
  const { data: sheet, error } = useLoad(() => getSheet(id), [id])
  const [outcome, setOutcome] = useState<Outcome | null>(null)
  const [chips, setChips] = useState<string[]>([])
  const [nextStep, setNextStep] = useState('Second meeting with the team')
  const [busy, setBusy] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)
  const [result, setResult] = useState<ClosureResponse | null>(null)

  const toggle = (c: string) => setChips((cs) => (cs.includes(c) ? cs.filter((x) => x !== c) : [...cs, c]))

  async function send() {
    if (!outcome) return
    setBusy(true)
    setActionError(null)
    try {
      setResult(await closeMeeting(id, { outcome, reason_chips: chips, next_step: outcome === 'next_step' ? nextStep : undefined }))
    } catch (e) {
      setActionError(e instanceof Error ? e.message : 'Could not send the answer.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <CompanyNav />
      <PageTitle title="Close within 72 hours" lead="Two taps: choose the outcome, then send. Everyone gets an answer." />
      {error && <Note tone="red">{error}</Note>}
      {actionError && <Note tone="red" role="alert">{actionError}</Note>}
      {!sheet && !error && <Loading />}

      {sheet && !result && (
        <Panel>
          <fieldset>
            <legend className="text-lg font-semibold">What happens next?</legend>
            <div className="mt-3 flex flex-wrap gap-3">
              {(['next_step', 'not_now'] as Outcome[]).map((o) => (
                <Button
                  key={o}
                  big
                  variant={outcome === o ? 'primary' : 'secondary'}
                  aria-pressed={outcome === o}
                  onClick={() => {
                    setOutcome(o)
                    setChips([])
                  }}
                >
                  {o === 'next_step' ? 'Next step' : 'Not now'}
                </Button>
              ))}
            </div>
          </fieldset>

          {outcome && (
            <fieldset className="mt-6">
              <legend className="font-medium">{outcome === 'next_step' ? 'What did you see? (optional)' : 'Which must-have was not shown yet?'}</legend>
              <div className="mt-2 flex flex-wrap gap-2">
                {sheet.questions.map((q) => (
                  <Button key={q.requirement_id} variant={chips.includes(q.requirement_id) ? 'primary' : 'secondary'} aria-pressed={chips.includes(q.requirement_id)} onClick={() => toggle(q.requirement_id)}>
                    {chips.includes(q.requirement_id) && <Check aria-hidden className="h-4 w-4" />}
                    {q.question}
                  </Button>
                ))}
              </div>
            </fieldset>
          )}

          {outcome === 'next_step' && (
            <label className="mt-4 flex flex-col gap-1 text-sm font-medium">
              Next step
              <input className={inputCls} value={nextStep} onChange={(e) => setNextStep(e.target.value)} />
            </label>
          )}

          {outcome && (
            <div className="mt-6">
              <Button big disabled={busy || (outcome === 'not_now' && chips.length === 0)} onClick={send}>
                {busy ? 'Sending…' : 'Send answer'} <ArrowRight aria-hidden className="h-4 w-4" />
              </Button>
            </div>
          )}
        </Panel>
      )}

      {result && (
        <div className="flex flex-col gap-4">
          <Panel>
            <h2 className="text-lg">Message to the talent</h2>
            <p className="mt-2 rounded-lg bg-snow p-4">{result.message_to_talent}</p>
          </Panel>
          {result.support_banner && (
            <div className="flex gap-3 rounded-lg border border-line border-l-4 border-l-moss bg-moss-tint p-4" role="note">
              <LifeBuoy aria-hidden className="mt-0.5 h-5 w-5 shrink-0 text-moss" />
              <div>
                <p className="font-medium">{result.support_banner}</p>
                <p className="mt-1 text-sm">Ask the TalentMatch desk or TE services in Espoo before you sign.</p>
              </div>
            </div>
          )}
          <Link to="/company/meetings" className="font-medium text-nordic underline underline-offset-2">
            Back to meetings
          </Link>
        </div>
      )}
    </div>
  )
}
