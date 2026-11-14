// Types mirror docs/03-product/api-contract.md (v1). Keep in sync with app/api.

export type Band = 'fewer than 10' | '10–19' | '20–49' | '50+'
export type Cefr = 'A1' | 'A2' | 'B1' | 'B2' | 'C1' | 'C2'
export const CEFR_LEVELS: Cefr[] = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2']

export type Provider = 'mock' | 'nvidia' | 'gemma'

export type LanguageNeed = { language: string; level: Cefr; task: string; from_when: string }

export type Requirement = {
  id: string
  text: string
  how_we_check: string
  esco_uri?: string
  esco_label?: string
}

export type LintHint = {
  id: string
  rule: string
  trigger: string
  requirement_id?: string
  why: string
  law?: string
  suggestion: string
  pool_before: Band
  pool_after: Band
}

export type Pool = {
  band: Band
  elasticity: { requirement_id: string; text: string; band_without: Band }[]
}

export type ChallengeCard = {
  id: string
  company_id: string
  title: string
  problem_90d: string
  must_haves: Requirement[]
  nice_to_haves: string[]
  languages: LanguageNeed[]
  work_mode: string
  status: 'draft' | 'approved'
  company_minutes_spent: number
}

export type TraceStep = { tool: string; input: unknown; output_summary: string; ms: number }

export type EvidenceLevel = 'own words' | 'artefact' | 'witnessed live'

export type Claim = {
  id: string
  text: string
  quote: string
  esco_uri?: string
  esco_label?: string
  evidence_level: EvidenceLevel
  confirmed: boolean
  original_language: string
  translated: boolean
}

export type PublicClaim = Omit<Claim, 'original_language' | 'translated'> &
  Partial<Pick<Claim, 'original_language' | 'translated'>>

export type EvidenceCard = {
  talent_id: string
  pseudonym: string
  headline: string
  claims: Claim[]
  languages: { language: string; level: Cefr }[]
  availability: string
}

export type SparkStatus = 'sent' | 'accepted' | 'declined' | 'refunded'

export type Spark = {
  id: string
  talent_id: string
  card_id: string
  claim_id: string
  requirement_id: string
  note?: string
  status: SparkStatus
  deadline: string
  revealed_name?: string
  slot?: string
}

// ---- Endpoint shapes ----

export type EventInfo = {
  id: string
  name: string
  date: string
  format: string
  companies_declared: number
  talents_registered_band: Band
}

export type Company = {
  id: string
  name: string
  size: number
  city: string
  contact_name: string
  slots: number
}

export type DraftResponse = {
  card: ChallengeCard
  followups: string[]
  lint: LintHint[]
  pool: Pool
  trace: TraceStep[]
  provider: Provider
}

export type Talent = {
  id: string
  pseudonym: string
  languages: { language: string; level: Cefr }[]
  availability: string
  spark_budget: number
  sparks_used: number
}

export type FollowupsResponse = { questions: string[]; provider: Provider }

export type ExtractResponse = {
  claims: Claim[]
  refused: { text: string; reason: string }[]
  provider: Provider
}

export type InboxSpark = {
  id: string
  pseudonym: string
  claim: PublicClaim
  note?: string
  status: SparkStatus
  deadline: string
  // Not in the contract list shape, but returned after accept in the UI state.
  revealed_name?: string
  slot?: string
}

export type CompanySparks = {
  by_requirement: { requirement: Requirement; sparks: InboxSpark[] }[]
  minutes_estimate: number
}

export type Meeting = { id: string; spark_id: string; talent_name: string; slot: string; card_id: string }

export type Tick = { requirement_id: string; seen: boolean; note?: string }

export type MeetingSheet = {
  meeting_id: string
  questions: { requirement_id: string; question: string; how_we_check: string }[]
  ticks: Tick[]
}

export type ClosureRequest = {
  outcome: 'next_step' | 'not_now'
  reason_chips: string[]
  next_step?: string
  redirect_company_id?: string
}

export type ClosureResponse = {
  closure: unknown
  message_to_talent: string
  support_banner?: string
}

export type OrganiserOverview = {
  cards_approved: number
  sparks_sent: number
  sparks_answered_pct: number
  meetings: number
  closures_within_72h_pct: number
  talents_without_meeting_band: Band
  avg_company_minutes: number
}

export type TwinReport = {
  runs: number
  pairs: number
  variants: { name: string; flip_rate_pct: number; n: number }[]
  threshold_pct: number
  passed: boolean
  placeholder?: boolean
  provider: Provider
  generated_at: string | null
  note?: string
}

export type AuditEvent = { at: string; actor: 'ai' | 'human'; action: string; detail: string }
