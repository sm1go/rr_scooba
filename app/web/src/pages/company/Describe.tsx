import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, FileText, ImageUp } from 'lucide-react'
import { draftCard } from '../../api'
import { SAMPLE_AD } from '../../fixtures/company'
import { COMPANY_ID, useDraft } from '../../state/company'
import { Button, Field, Note, PageTitle, Panel, SuggestedLabel, inputCls } from '../../components/ui'
import CompanyNav from './nav'
import Trace from './Trace'

function readAsBase64(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const r = new FileReader()
    r.onload = () => resolve(String(r.result).split(',')[1] ?? '')
    r.onerror = () => reject(r.error)
    r.readAsDataURL(file)
  })
}

export default function Describe() {
  const { draft, setDraft } = useDraft()
  const navigate = useNavigate()
  const [text, setText] = useState('')
  const [file, setFile] = useState<File | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function submit() {
    setBusy(true)
    setError(null)
    try {
      const image_base64 = file ? await readAsBase64(file) : undefined
      const res = await draftCard({ company_id: COMPANY_ID, text: text.trim() || undefined, image_base64 })
      setDraft(res)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not draft the card.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <CompanyNav />
      <PageTitle
        step="Lumo Systems Oy · Sanna Virtanen"
        title="Describe your need"
        lead="Paste last year's job ad or upload a screenshot. The assistant turns it into a Challenge Card: one problem, three must-haves. You check and edit everything."
      />

      <Panel>
        <div className="flex flex-col gap-4">
          <Field id="ad" label="Last year's job ad" hint="Plain text is fine. Do not include names or contact details.">
            <textarea
              id="ad"
              aria-describedby="ad-hint"
              rows={9}
              className={inputCls}
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </Field>
          <div className="flex flex-wrap items-center gap-3">
            <Button variant="secondary" disabled={Boolean(text.trim())} onClick={() => setText(SAMPLE_AD)}>
              <FileText aria-hidden className="h-4 w-4" /> Use sample ad
            </Button>
            <label className="inline-flex min-h-10 cursor-pointer items-center gap-2 rounded-lg border border-nordic bg-white px-4 text-sm font-medium text-nordic hover:bg-lake focus-within:outline-3 focus-within:outline-nordic">
              <ImageUp aria-hidden className="h-4 w-4" />
              {file ? `Screenshot: ${file.name}` : 'Upload a screenshot'}
              <input type="file" accept="image/*" className="sr-only" onChange={(e) => setFile(e.target.files?.[0] ?? null)} />
            </label>
          </div>
          {file && <p className="text-sm text-muted">Please remove names and contact details from the screenshot before uploading it.</p>}
          <div>
            <Button big disabled={busy || (!text.trim() && !file)} onClick={submit}>
              {busy ? 'Drafting…' : 'Draft my Challenge Card'}
            </Button>
          </div>
          {error && <Note tone="red">{error}</Note>}
        </div>
      </Panel>

      {draft && (
        <Panel className="mt-6">
          <h2 className="text-lg">What the assistant did</h2>
          <SuggestedLabel why="The assistant read your ad and used a few tools: a skills list (ESCO), a fairness rulebook and a privacy-safe pool count. Nothing is published until you approve it." />
          <Trace steps={draft.trace} />
          {draft.followups.length > 0 && (
            <div className="mt-4">
              <h3 className="text-base">Questions to think about</h3>
              <ul className="mt-1 list-disc pl-6 text-muted">
                {draft.followups.map((q) => (
                  <li key={q}>{q}</li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-6">
            <Button big onClick={() => navigate('/company/card')}>
              Check my card <ArrowRight aria-hidden className="h-4 w-4" />
            </Button>
          </div>
        </Panel>
      )}
    </div>
  )
}
