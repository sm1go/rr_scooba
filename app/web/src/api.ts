// Typed client for docs/03-product/api-contract.md.
// Every call falls back to local synthetic fixtures when the backend is not reachable,
// and flips a global "offline" flag that the UI shows as a quiet badge.
import * as co from './fixtures/company'
import * as ta from './fixtures/talent'
import type {
  AuditEvent,
  ChallengeCard,
  Claim,
  ClosureRequest,
  ClosureResponse,
  Company,
  CompanySparks,
  DraftResponse,
  EventInfo,
  EvidenceCard,
  ExtractResponse,
  FollowupsResponse,
  LintHint,
  Meeting,
  MeetingSheet,
  OrganiserOverview,
  Pool,
  Spark,
  Talent,
  Tick,
  TwinReport,
} from './types'

// ---------- offline flag (tiny external store) ----------
let offline = false
const listeners = new Set<() => void>()
function setOffline(v: boolean) {
  if (offline !== v) {
    offline = v
    listeners.forEach((l) => l())
  }
}
export const offlineStore = {
  subscribe(l: () => void) {
    listeners.add(l)
    return () => listeners.delete(l)
  },
  get: () => offline,
}

export class ApiError extends Error {
  status: number
  constructor(status: number, message: string) {
    super(message)
    this.status = status
  }
}

/** Fetch JSON; on network error, proxy error (non-JSON) or 5xx use the fallback. JSON 4xx errors are thrown as ApiError. */
async function call<T>(method: 'GET' | 'POST', path: string, body: unknown, fallback: () => T): Promise<T> {
  let res: Response
  try {
    res = await fetch(`/api${path}`, {
      method,
      headers: body !== undefined ? { 'Content-Type': 'application/json' } : undefined,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    })
  } catch {
    setOffline(true)
    return fallback()
  }
  const isJson = (res.headers.get('content-type') ?? '').includes('application/json')
  if (res.ok && isJson) {
    setOffline(false)
    return (await res.json()) as T
  }
  // A real client error should never be disguised as offline demo data.
  if (res.status >= 400 && res.status < 500) {
    let msg = res.statusText
    if (isJson) {
      try {
        const j = await res.json()
        const d = j.detail
        msg = typeof d === 'string' ? d : typeof d?.detail === 'string' ? d.detail : msg
      } catch {
        /* ignore */
      }
    } else {
      const text = (await res.text()).trim()
      if (text) msg = text.slice(0, 200)
    }
    throw new ApiError(res.status, msg)
  }
  setOffline(true)
  return fallback()
}

// ---------- in-memory offline state so the demo still flows ----------
const local = {
  cards: [...co.approvedCards] as ChallengeCard[],
  talentSparks: [{
    id: 'sp-local-1',
    talent_id: 'ta-0427',
    card_id: 'card-co-lumo',
    claim_id: 'cl-amira-build',
    requirement_id: 'req-lumo-1',
    note: 'Your 40-minute pipeline sounds like the one I fixed.',
    status: 'sent' as const,
    deadline: '2026-11-20T16:00:00+02:00',
  }] as Spark[],
  inbox: structuredClone(co.companySparks) as CompanySparks,
  meetings: [...co.meetings] as Meeting[],
  sheets: Object.fromEntries(
    co.meetings.map((m) => [m.id, { ...structuredClone(co.meetingSheet), meeting_id: m.id }]),
  ) as Record<string, MeetingSheet>,
  evidence: ta.evidenceCard as EvidenceCard,
  sparksUsed: 1,
}

// ---------- company ----------
export const getEvent = () => call<EventInfo>('GET', '/event', undefined, () => co.eventInfo)
export const getCompany = (id: string) => call<Company>('GET', `/companies/${id}`, undefined, () => co.lumo)

export const draftCard = (body: { company_id: string; text?: string; image_base64?: string }) =>
  call<DraftResponse>('POST', '/compiler/draft', body, () => structuredClone(co.draftResponse))

export const lint = (card: ChallengeCard) =>
  call<{ hints: LintHint[] }>('POST', '/lint', { card }, () => ({ hints: co.offlineLint(card) }))

export const pool = (card: ChallengeCard) => call<Pool>('POST', '/pool', { card }, () => co.offlinePool(card))

export const approveCard = (card: ChallengeCard) =>
  call<ChallengeCard>('POST', '/cards', { card }, () => {
    const approved = { ...card, status: 'approved' as const }
    local.cards = [approved, ...local.cards.filter((c) => c.id !== card.id)]
    return approved
  })

export const getCard = (id: string) =>
  call<ChallengeCard>('GET', `/cards/${id}`, undefined, () => local.cards.find((c) => c.id === id) ?? local.cards[0])

export const listCards = () => call<ChallengeCard[]>('GET', '/cards', undefined, () => local.cards)

// ---------- talent ----------
export const getTalent = (id: string) =>
  call<Talent>('GET', `/talents/${id}`, undefined, () => ({ ...ta.talent, sparks_used: local.sparksUsed }))

export const storyFollowups = (body: { talent_id: string; transcript: string; language: string }) =>
  call<FollowupsResponse>('POST', '/story/followups', body, () => ta.followups)

export const storyExtract = (body: { talent_id: string; transcript: string; language: string }) =>
  call<ExtractResponse>('POST', '/story/extract', body, () => ta.offlineExtract(body.transcript))

export const saveEvidence = (talentId: string, claims: Claim[]) =>
  call<EvidenceCard>('POST', `/evidence/${talentId}`, { claims }, () => {
    local.evidence = ta.offlineEvidence(claims)
    return local.evidence
  })

export const getEvidence = (talentId: string) =>
  call<EvidenceCard>('GET', `/evidence/${talentId}`, undefined, () => local.evidence)

// ---------- sparks & meetings ----------
export const getTalentSparks = (talentId: string) =>
  call<Spark[]>('GET', `/talents/${talentId}/sparks`, undefined, () => local.talentSparks)

export const sendSpark = (body: { talent_id: string; card_id: string; claim_id: string; requirement_id: string; note?: string }) =>
  call<Spark>('POST', '/sparks', body, () => {
    if (local.sparksUsed >= ta.talent.spark_budget) throw new ApiError(409, 'All your Sparks are in use.')
    local.sparksUsed += 1
    const s: Spark = { id: `sp-local-${Date.now()}`, ...body, status: 'sent', deadline: '2026-11-20T16:00:00+02:00' }
    local.talentSparks = [s, ...local.talentSparks]
    const card = local.cards.find((c) => c.id === body.card_id)
    const requirement = card?.must_haves.find((r) => r.id === body.requirement_id)
    const claim = local.evidence.claims.find((c) => c.id === body.claim_id)
    if (card && requirement && claim) {
      let group = local.inbox.by_requirement.find((g) => g.requirement.id === requirement.id)
      if (!group) {
        group = { requirement, sparks: [] }
        local.inbox.by_requirement.push(group)
      }
      group.sparks.unshift({
        id: s.id,
        pseudonym: ta.talent.pseudonym,
        claim,
        note: body.note,
        status: 'sent',
        deadline: s.deadline,
      })
    }
    return s
  })

export const getCompanySparks = (companyId: string) =>
  call<CompanySparks>('GET', `/companies/${companyId}/sparks`, undefined, () => local.inbox)

const OFFLINE_NAMES: Record<string, string> = { 'Talent #0427': 'Amira Haddad', 'Talent #0193': 'Jonas Lind', 'Talent #0211': 'Aino Mäki' }

export const respondSpark = (id: string, body: { decision: 'accept' | 'decline'; reason_chip?: string }) =>
  call<Spark>('POST', `/sparks/${id}/respond`, body, () => {
    const item = local.inbox.by_requirement.flatMap((g) => g.sparks).find((s) => s.id === id)
    const group = local.inbox.by_requirement.find((g) => g.sparks.some((s) => s.id === id))
    const sent = local.talentSparks.find((s) => s.id === id) ?? (item ? {
      id: item.id,
      talent_id: item.pseudonym === 'Talent #0427' ? 'ta-0427' : 'ta-0193',
      card_id: 'card-co-lumo',
      claim_id: item.claim.id,
      requirement_id: group?.requirement.id ?? '',
      note: item.note,
      status: 'sent' as const,
      deadline: item.deadline,
    } : undefined)
    if (!item || !sent) throw new ApiError(404, 'Spark not found in this demo.')
    const accepted = body.decision === 'accept'
    if (accepted && local.meetings.length >= co.lumo.slots)
      throw new ApiError(409, 'This company has no meeting slots left.')
    const slot = accepted ? `Thu 26 Nov · ${10 + Math.floor(local.meetings.length / 3)}:${String((local.meetings.length % 3) * 20).padStart(2, '0')}` : undefined
    const spark: Spark = {
      id,
      talent_id: sent.talent_id,
      card_id: sent.card_id,
      claim_id: sent.claim_id,
      requirement_id: sent.requirement_id,
      note: sent.note,
      status: accepted ? 'accepted' : 'declined',
      deadline: item.deadline,
      revealed_name: accepted ? (OFFLINE_NAMES[item?.pseudonym ?? ''] ?? 'Synthetic Person') : undefined,
      slot,
    }
    if (item) Object.assign(item, { status: spark.status, revealed_name: spark.revealed_name, slot })
    local.talentSparks = local.talentSparks.map((s) => s.id === id ? spark : s)
    if (!accepted) local.sparksUsed = Math.max(0, local.sparksUsed - 1)
    if (accepted && spark.revealed_name && slot) {
      const meetingId = `mt-local-${id}`
      local.meetings = [...local.meetings, { id: meetingId, spark_id: id, talent_name: spark.revealed_name, slot, card_id: sent.card_id }]
      local.sheets[meetingId] = { ...structuredClone(co.meetingSheet), meeting_id: meetingId }
    }
    return spark
  })

export const getMeetings = (companyId: string) =>
  call<Meeting[]>('GET', `/companies/${companyId}/meetings`, undefined, () => local.meetings)

export const getSheet = (meetingId: string) =>
  call<MeetingSheet>('GET', `/meetings/${meetingId}/sheet`, undefined, () => {
    local.sheets[meetingId] ??= { ...structuredClone(co.meetingSheet), meeting_id: meetingId }
    return local.sheets[meetingId]
  })

export const saveTicks = (meetingId: string, ticks: Tick[]) =>
  call<MeetingSheet>('POST', `/meetings/${meetingId}/ticks`, { ticks }, () => {
    local.sheets[meetingId] ??= { ...structuredClone(co.meetingSheet), meeting_id: meetingId }
    local.sheets[meetingId] = { ...local.sheets[meetingId], ticks }
    return local.sheets[meetingId]
  })

export const closeMeeting = (meetingId: string, body: ClosureRequest) =>
  call<ClosureResponse>('POST', `/meetings/${meetingId}/closure`, body, () => ({
    closure: { meeting_id: meetingId, ...body },
    message_to_talent:
      body.outcome === 'next_step'
        ? `Thank you for meeting Lumo Systems Oy. We'd like to move forward — next step: ${body.next_step || 'a second meeting'}.`
        : `Thank you for meeting Lumo Systems Oy. This time we are not moving forward (${body.reason_chips.length} requirement(s) not shown yet).`,
    support_banner: body.outcome === 'next_step' ? "Pay subsidy or other support may apply — don't sign before the decision." : undefined,
  }))

// ---------- organiser ----------
export const getOverview = () => call<OrganiserOverview>('GET', '/organiser/overview', undefined, () => ta.overview)
export const getTwinReport = () => call<TwinReport>('GET', '/trust/twin-report', undefined, () => ta.twinReport)
export const getAudit = () => call<AuditEvent[]>('GET', '/audit', undefined, () => ta.audit)
