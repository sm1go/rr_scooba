import { useState } from 'react'
import { Link } from 'react-router-dom'
import { ArrowRight, Check, CheckCircle2, FileText, Mic, X } from 'lucide-react'
import { saveEvidence, storyExtract, storyFollowups } from '../../api'
import { SAMPLE_STORY } from '../../fixtures/talent'
import { TALENT_ID } from '../../state/company'
import { langName } from '../../format'
import type { Claim, EvidenceCard, ExtractResponse } from '../../types'
import { EvidenceChip } from '../../components/ClaimView'
import { Button, Chip, Field, Note, PageTitle, Panel, SuggestedLabel, inputCls } from '../../components/ui'
import TalentNav from './nav'

const LANGS = [
  { code: 'en', name: 'English' },
  { code: 'ar', name: 'Arabic' },
  { code: 'fi', name: 'Finnish' },
  { code: 'uk', name: 'Ukrainian' },
  { code: 'ru', name: 'Russian' },
  { code: 'so', name: 'Somali' },
]

/** Show the quote inside its surrounding words so the person sees it really came from them. */
function QuoteInContext({ transcript, quote, lang }: { transcript: string; quote: string; lang: string }) {
  const i = transcript.indexOf(quote)
  if (i < 0) return <mark lang={lang}>{quote}</mark>
  const before = transcript.slice(Math.max(0, i - 50), i)
  const after = transcript.slice(i + quote.length, i + quote.length + 50)
  return (
    <p className="text-sm text-muted" lang={lang}>
      {i > 50 && '…'}
      {before}
      <mark>{quote}</mark>
      {after}
      {i + quote.length + 50 < transcript.length && '…'}
    </p>
  )
}

export default function Story() {
  const [transcript, setTranscript] = useState('')
  const [lang, setLang] = useState('en')
  const [questions, setQuestions] = useState<string[] | null>(null)
  const [result, setResult] = useState<ExtractResponse | null>(null)
  const [claims, setClaims] = useState<Claim[]>([])
  const [saved, setSaved] = useState<EvidenceCard | null>(null)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const language = LANGS.find((l) => l.code === lang)?.name ?? 'English'
  const body = { talent_id: TALENT_ID, transcript, language }

  async function run<T>(fn: () => Promise<T>, then: (v: T) => void) {
    setBusy(true)
    setError(null)
    try {
      then(await fn())
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not process this story. Please try again.')
    } finally {
      setBusy(false)
    }
  }

  const toggle = (id: string) => setClaims((cs) => cs.map((c) => (c.id === id ? { ...c, confirmed: !c.confirmed } : c)))

  return (
    <div className="mx-auto max-w-xl">
      <TalentNav />
      <PageTitle step="Talent #0427" title="Tell a work story" lead="Write about one thing you did at work, in the language you know best. We only keep what is in your own words." />
      {error && <Note tone="red" role="alert">{error}</Note>}

      {saved ? (
        <Panel>
          <p className="flex items-center gap-2 text-lg font-semibold text-moss">
            <CheckCircle2 aria-hidden className="h-5 w-5" /> Your evidence card is saved
          </p>
          <p className="mt-2">{saved.headline}</p>
          <ul className="mt-3 list-disc pl-6">
            {saved.claims.map((c) => (
              <li key={c.id}>{c.text}</li>
            ))}
          </ul>
          <p className="mt-3 text-sm text-muted">Companies see your pseudonym “{saved.pseudonym}”, not your name.</p>
          <Link to="/talent/sparks" className="mt-4 inline-flex min-h-12 items-center gap-2 rounded-lg bg-nordic px-6 font-medium text-white hover:bg-nordic-dark">
            Send a Spark <ArrowRight aria-hidden className="h-4 w-4" />
          </Link>
        </Panel>
      ) : !result ? (
        <Panel>
          <div className="flex flex-col gap-4">
            <Field id="lang" label="Language of your story">
              <select id="lang" className={inputCls} value={lang} onChange={(e) => setLang(e.target.value)}>
                {LANGS.map((l) => (
                  <option key={l.code} value={l.code}>
                    {l.name}
                  </option>
                ))}
              </select>
            </Field>
            <Field id="story" label="Your work story" hint="What was the problem? What did you do? What changed?">
              <textarea id="story" aria-describedby="story-hint" lang={lang} dir={lang === 'ar' ? 'rtl' : 'ltr'} rows={8} className={inputCls} value={transcript} onChange={(e) => setTranscript(e.target.value)} />
            </Field>
            <p className="inline-flex items-center gap-2 text-sm text-muted">
              <Mic aria-hidden className="h-4 w-4" /> Voice optional — typing works the same.
            </p>
            <div>
              <Button variant="secondary" disabled={Boolean(transcript.trim())} onClick={() => { setTranscript(SAMPLE_STORY); setLang('en') }}>
                <FileText aria-hidden className="h-4 w-4" /> Use sample story
              </Button>
            </div>

            {questions && questions.length > 0 && (
              <div className="rounded-lg bg-lake p-4">
                <p className="font-medium">A few questions that may help (add answers to your story if you like):</p>
                <ol className="mt-2 list-decimal pl-6">
                  {questions.slice(0, 3).map((q) => (
                    <li key={q}>{q}</li>
                  ))}
                </ol>
                <div className="mt-2">
                  <SuggestedLabel />
                </div>
              </div>
            )}

            {questions === null ? (
              <Button big disabled={busy || !transcript.trim()} onClick={() => run(() => storyFollowups(body), (r) => setQuestions(r.questions))}>
                {busy ? 'Reading…' : 'Continue'}
              </Button>
            ) : (
              <Button
                big
                disabled={busy || !transcript.trim()}
                onClick={() => run(() => storyExtract(body), (r) => { setResult(r); setClaims(r.claims) })}
              >
                {busy ? 'Finding…' : 'Find what I can show'}
              </Button>
            )}
          </div>
        </Panel>
      ) : (
        <div className="flex flex-col gap-4">
          <SuggestedLabel why="The assistant only suggests claims backed by an exact quote from your story. You confirm or remove each one." />
          <ul className="flex flex-col gap-3">
            {claims.map((c) => (
              <li key={c.id} className={`rounded-lg border bg-white p-4 ${c.confirmed ? 'border-line' : 'border-dashed border-line opacity-75'}`}>
                <p className="font-medium">{c.text}</p>
                <div className="mt-2">
                  <QuoteInContext transcript={transcript} quote={c.quote} lang={lang} />
                </div>
                <div className="mt-2 flex flex-wrap gap-2">
                  <EvidenceChip level={c.evidence_level} />
                  {c.translated && <Chip>Translated from {langName(c.original_language)}</Chip>}
                </div>
                <div className="mt-3 flex gap-2" role="group" aria-label={`Keep “${c.text}”?`}>
                  <Button variant={c.confirmed ? 'primary' : 'secondary'} aria-pressed={c.confirmed} onClick={() => !c.confirmed && toggle(c.id)}>
                    <Check aria-hidden className="h-4 w-4" /> Confirm
                  </Button>
                  <Button variant={!c.confirmed ? 'primary' : 'secondary'} aria-pressed={!c.confirmed} onClick={() => c.confirmed && toggle(c.id)}>
                    <X aria-hidden className="h-4 w-4" /> Remove
                  </Button>
                </div>
              </li>
            ))}
          </ul>
          {result.refused.map((r) => (
            <Note key={r.text}>
              <p className="font-medium">We couldn't find this in your words: “{r.text}”</p>
              <p className="mt-1">{r.reason}</p>
            </Note>
          ))}
          {claims.length === 0 && <p className="text-muted">We did not find a claim yet. Try adding what you did and what changed.</p>}
          <div className="flex flex-wrap gap-3">
            <Button big disabled={busy || !claims.some((c) => c.confirmed)} onClick={() => run(() => saveEvidence(TALENT_ID, claims.filter((c) => c.confirmed)), setSaved)}>
              {busy ? 'Saving…' : 'Save my evidence card'}
            </Button>
            <Button variant="quiet" onClick={() => setResult(null)}>
              Edit my story
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
