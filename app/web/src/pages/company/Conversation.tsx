import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getSheet, saveTicks } from '../../api'
import type { Tick } from '../../types'
import { Button, Loading, Note, PageTitle, Panel, inputCls } from '../../components/ui'
import { useLoad } from '../../useLoad'
import CompanyNav from './nav'

export default function Conversation() {
  const { id = '' } = useParams()
  const navigate = useNavigate()
  const { data, setData, error } = useLoad(() => getSheet(id), [id])
  const [busy, setBusy] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const tickFor = (rid: string): Tick => data?.ticks.find((t) => t.requirement_id === rid) ?? { requirement_id: rid, seen: false }
  function setTick(rid: string, patch: Partial<Tick>) {
    if (!data) return
    const others = data.ticks.filter((t) => t.requirement_id !== rid)
    setData({ ...data, ticks: [...others, { ...tickFor(rid), ...patch }] })
  }

  async function saveAndClose() {
    if (!data) return
    setBusy(true)
    setActionError(null)
    try {
      await saveTicks(id, data.questions.map((q) => tickFor(q.requirement_id)))
      navigate(`/company/meetings/${id}/closure`)
    } catch (e) {
      setActionError(e instanceof Error ? e.message : 'Could not save the conversation.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <CompanyNav />
      <PageTitle
        title="Conversation sheet"
        lead="Ask every person the same three questions. Tick what you saw. The talent can see these ticks."
      />
      {error && <Note tone="red">{error}</Note>}
      {actionError && <Note tone="red" role="alert">{actionError}</Note>}
      {!data && !error && <Loading />}
      {data && (
        <>
          <ol className="flex flex-col gap-4">
            {data.questions.map((q, i) => {
              const t = tickFor(q.requirement_id)
              return (
                <li key={q.requirement_id}>
                  <Panel>
                    <h2 className="text-lg">
                      {i + 1}. {q.question}
                    </h2>
                    <p className="mt-1 text-muted">Ask: {q.how_we_check}</p>
                    <label className="mt-3 flex min-h-10 cursor-pointer items-center gap-3">
                      <input
                        type="checkbox"
                        className="h-5 w-5 accent-[#0050B5]"
                        checked={t.seen}
                        onChange={(e) => setTick(q.requirement_id, { seen: e.target.checked })}
                      />
                      <span className="font-medium">Seen in the conversation</span>
                    </label>
                    <label className="mt-2 flex flex-col gap-1 text-sm">
                      Note (optional, about the work only)
                      <input className={inputCls} value={t.note ?? ''} onChange={(e) => setTick(q.requirement_id, { note: e.target.value })} />
                    </label>
                  </Panel>
                </li>
              )
            })}
          </ol>
          <div className="mt-6">
            <Button big disabled={busy} onClick={saveAndClose}>
              {busy ? 'Saving…' : 'Save and close the conversation'}
            </Button>
          </div>
        </>
      )}
    </div>
  )
}
