import type { AuditEvent, Claim, EvidenceCard, ExtractResponse, OrganiserOverview, Spark, Talent, TwinReport } from '../types'

export const SAMPLE_STORY = `In my previous team at a payments company, our release builds took 30 minutes and everyone complained but nobody owned it. I helped cut our build time from 30 to 6 minutes by caching the dependencies and splitting the test suite so the slow parts run in parallel. I wrote most of the pytest suite we still run today, and I built the FastAPI service that handles our payments. I also helped the team move to small daily releases instead of the big monthly one.`

export const talent: Talent = {
  id: 'ta-0427',
  pseudonym: 'Talent #0427',
  languages: [
    { language: 'Arabic', level: 'C2' },
    { language: 'English', level: 'B2' },
    { language: 'Finnish', level: 'B1' },
  ],
  availability: 'immediately',
  spark_budget: 3,
  sparks_used: 0,
}

export const followups = {
  questions: [
    'You said the build dropped from 30 to 6 minutes — what exactly did you change?',
    "Was splitting the test suite your idea or the team's?",
    'Can you remember a time a fast build saved a release?',
  ],
  provider: 'mock' as const,
}

const amiraClaim = (id: string, text: string, esco_label: string): Claim => ({
  id,
  text,
  quote: text,
  esco_label,
  evidence_level: 'own words',
  confirmed: false,
  original_language: 'ar',
  translated: true,
})

/** Offline extract: only quotes that are exact substrings of the transcript survive. */
export function offlineExtract(transcript: string): ExtractResponse {
  const candidates: Claim[] = [
    amiraClaim('cl-amira-build', 'I helped cut our build time from 30 to 6 minutes', 'use continuous integration and delivery tools'),
    amiraClaim('cl-amira-pytest', 'I wrote most of the pytest suite we still run today', 'develop automated software tests'),
    amiraClaim('cl-amira-fastapi', 'I built the FastAPI service that handles our payments', 'develop software in Python'),
  ]
  const claims = candidates.filter((c) => transcript.includes(c.quote))
  const refused = claims.length
    ? [
        { text: 'Led the CI/CD transformation and owned the release pipeline end-to-end', reason: "Your words say 'helped', not 'led' or 'owned'. We kept your own word." },
        { text: 'Expert in Kubernetes cluster operations', reason: 'Nothing in your story talks about this.' },
      ]
    : []
  return { claims, refused, provider: 'mock' }
}

export function offlineEvidence(claims: Claim[]): EvidenceCard {
  return {
    talent_id: 'ta-0427',
    pseudonym: 'Talent #0427',
    headline: 'Backend engineer — I make builds fast',
    claims: claims.filter((c) => c.confirmed),
    languages: talent.languages,
    availability: talent.availability,
  }
}

export const evidenceCard: EvidenceCard = offlineEvidence(offlineExtract(SAMPLE_STORY).claims)

export const mySparks: Spark[] = []

export const overview: OrganiserOverview = {
  cards_approved: 12,
  sparks_sent: 214,
  sparks_answered_pct: 81,
  meetings: 63,
  closures_within_72h_pct: 74,
  talents_without_meeting_band: '50+',
  avg_company_minutes: 38,
}

export const twinReport: TwinReport = {
  runs: 2,
  pairs: 1000,
  variants: [
    { name: 'plain vs AI-polished prose', flip_rate_pct: 2.1, n: 1000 },
    { name: 'Finnish name vs international name', flip_rate_pct: 1.4, n: 1000 },
    { name: 'Finnish vs Arabic strongest language', flip_rate_pct: 3.0, n: 1000 },
  ],
  threshold_pct: 5,
  passed: false,
  placeholder: true,
  provider: 'mock',
  generated_at: null,
  note: 'No fairness batch has run yet. This demo does not claim a fairness result.',
}

export const audit: AuditEvent[] = [
  { at: '2026-11-14T09:12:04+02:00', actor: 'ai', action: 'card.draft', detail: 'Drafted Challenge Card card-co-lumo-draft from pasted ad' },
  { at: '2026-11-14T09:12:05+02:00', actor: 'ai', action: 'lint.hint', detail: 'Flagged "Fluent Finnish" (no task given)' },
  { at: '2026-11-14T09:15:40+02:00', actor: 'human', action: 'card.edit', detail: 'Sanna applied suggestion: Finnish B1 for customer calls by month 6' },
  { at: '2026-11-14T09:16:02+02:00', actor: 'human', action: 'card.approve', detail: 'Sanna approved card-co-lumo' },
  { at: '2026-11-14T10:02:11+02:00', actor: 'ai', action: 'story.extract', detail: 'Extracted 3 quote-backed claims for ta-0427, refused 1 inflated claim' },
  { at: '2026-11-14T10:04:30+02:00', actor: 'human', action: 'evidence.confirm', detail: 'Talent #0427 confirmed 3 claims' },
]
