# API contract v1 — TalentMatch Signal MVP

Single source of truth between `app/api` (FastAPI) and `app/web` (React). All JSON, prefix `/api`,
dev server `http://127.0.0.1:8000`, Vite dev server `http://127.0.0.1:5173` with proxy `/api` → 8000.
Synthetic data only. IDs are strings. Times ISO 8601, Europe/Helsinki.

## Fixed demo world (seeded, deterministic)

- Event `ev-2026-11` — "TalentMatch Espoo · Tech & ICT", hybrid, 2026-11-26, 40 companies declared,
  slots per company declared in `company.slots`.
- Company `co-lumo` — "Lumo Systems Oy", 14 people, Espoo; contact persona **Sanna Virtanen** (founder).
- Talent `ta-0427` — persona **Amira Haddad**, backend engineer; public pseudonym "Talent #0427".
- ~300 synthetic talents, ~12 companies with approved cards, other demo companies with Sparks inbox.

## Shared types

```ts
type Band = "fewer than 10" | "10–19" | "20–49" | "50+";
type Cefr = "A1"|"A2"|"B1"|"B2"|"C1"|"C2";
type LanguageNeed = { language: string; level: Cefr; task: string; from_when: string }; // e.g. Finnish, B1, "customer calls", "by month 6"
type Requirement = { id: string; text: string; how_we_check: string; esco_uri?: string; esco_label?: string };
type LintHint = { id: string; rule: string; trigger: string; requirement_id?: string;
                  why: string; law?: string; suggestion: string; pool_before: Band; pool_after: Band };
type Pool = { band: Band; elasticity: { requirement_id: string; text: string; band_without: Band }[] };
type ChallengeCard = { id: string; company_id: string; title: string; problem_90d: string;
                       must_haves: Requirement[]; nice_to_haves: string[]; languages: LanguageNeed[];
                       work_mode: string; status: "draft"|"approved"; company_minutes_spent: number };
type TraceStep = { tool: string; input: any; output_summary: string; ms: number };
type Claim = { id: string; text: string; quote: string; esco_uri?: string; esco_label?: string;
               evidence_level: "own words"|"artefact"|"witnessed live"; confirmed: boolean;
               original_language: string; translated: boolean };
type EvidenceCard = { talent_id: string; pseudonym: string; headline: string; claims: Claim[];
                      languages: { language: string; level: Cefr }[]; availability: string };
type Spark = { id: string; talent_id: string; card_id: string; claim_id: string; requirement_id: string;
               note?: string; status: "sent"|"accepted"|"declined"|"refunded"; deadline: string;
               revealed_name?: string; slot?: string };
```

`provider` on AI responses: `"mock"` (recorded fallback) | `"nvidia"` | `"gemma"`.

## Company side (F01, F02, F03)

| Method | Path | Body → Response |
|---|---|---|
| GET | `/api/event` | → `{ id, name, date, format, companies_declared, talents_registered_band: Band }` |
| GET | `/api/companies/{id}` | → `{ id, name, size, city, contact_name, slots }` |
| POST | `/api/compiler/draft` | `{ company_id, text?: string, image_base64?: string }` → `{ card: ChallengeCard, followups: string[], lint: LintHint[], pool: Pool, trace: TraceStep[], provider }` |
| POST | `/api/lint` | `{ card: ChallengeCard }` → `{ hints: LintHint[] }` (deterministic rulebook, max 5) |
| POST | `/api/pool` | `{ card: ChallengeCard }` → `Pool` (deterministic, k = 10 bands, never people) |
| POST | `/api/cards` | `{ card: ChallengeCard }` → `ChallengeCard` with `status:"approved"` |
| GET | `/api/cards/{id}` | → `ChallengeCard` |
| GET | `/api/cards` | → `ChallengeCard[]` (approved cards for the event; talent side browses these) |

## Talent side (F04)

| Method | Path | Body → Response |
|---|---|---|
| GET | `/api/talents/{id}` | → `{ id, pseudonym, languages, availability, spark_budget, sparks_used }` (never the name) |
| POST | `/api/story/followups` | `{ talent_id, transcript, language }` → `{ questions: string[] (≤3), provider }` |
| POST | `/api/story/extract` | `{ talent_id, transcript, language }` → `{ claims: Claim[], refused: { text, reason }[], provider }` — server rejects any claim whose quote is not an exact substring of the transcript, and inflated verbs ("led" when the quote says "helped"); returned claims have `confirmed:false` until the person confirms them |
| POST | `/api/evidence/{talent_id}` | `{ claims: Claim[] }` (only confirmed ones kept) → `EvidenceCard` |
| GET | `/api/evidence/{talent_id}` | → `EvidenceCard` |

## Sparks (F06) and meetings (F08-lite, F10, F13, F14)

| Method | Path | Body → Response |
|---|---|---|
| GET | `/api/talents/{id}/sparks` | → `Spark[]` |
| POST | `/api/sparks` | `{ talent_id, card_id, claim_id, requirement_id, note? (≤140 chars) }` → `Spark` (409 if budget used; budget = min(5, max(3, round(total_company_slots × 1.5 / talents_registered)))) |
| GET | `/api/companies/{id}/sparks` | → `{ by_requirement: { requirement: Requirement, sparks: { id, pseudonym, claim: Claim, note?, status, deadline }[] }[], minutes_estimate: number }` — no names or source-language metadata before accept |
| POST | `/api/sparks/{id}/respond` | `{ decision: "accept"|"decline", reason_chip?: string }` → `Spark` (accept → `revealed_name` + first free `slot`; decline → refunded to talent) |
| GET | `/api/companies/{id}/meetings` | → `{ id, spark_id, talent_name, slot, card_id }[]` |
| GET | `/api/meetings/{id}/sheet` | → `{ meeting_id, questions: { requirement_id, question: string, how_we_check }[] (exactly the card must-haves), ticks: { requirement_id, seen: boolean, note? }[] }` |
| POST | `/api/meetings/{id}/ticks` | `{ ticks: { requirement_id, seen, note? }[] }` → sheet |
| POST | `/api/meetings/{id}/closure` | `{ outcome: "next_step"|"not_now", reason_chips: string[], next_step?: string, redirect_company_id?: string }` → `{ closure, message_to_talent: string, support_banner?: string }` — reason chips must come from the card requirements; support banner: "Pay subsidy or other support may apply — don't sign before the decision." |

## Organiser and trust (F15/F16 tile, F18)

| Method | Path | Response |
|---|---|---|
| GET | `/api/organiser/overview` | `{ cards_approved, sparks_sent, sparks_answered_pct, meetings, closures_within_72h_pct, talents_without_meeting_band: Band, avg_company_minutes }` |
| GET | `/api/trust/twin-report` | `{ runs, pairs, variants: { name, flip_rate_pct, n }[], threshold_pct, passed, placeholder, provider, generated_at }`; before the Modal batch runs, `placeholder:true`, `passed:false`, and `variants:[]` |
| GET | `/api/audit` | last 50 audit events `{ at, actor: "ai"|"human", action, detail }` |

## Rules (deterministic, unit-tested)

- Pool bands use only *confirmed* claims of talents with pool consent; counts < 10 → "fewer than 10".
- Lint rulebook triggers: native speaker / mother tongue, fluent Finnish without a task, nationality /
  citizenship, age words ("young", "digital native"), gendered words, photo, degree without a reason,
  "no gaps", "cultural fit". Each hint carries the law (Non-Discrimination Act 1325/2014, Equality Act 609/1986) where relevant.
- No endpoint returns a score, rank or ordered list of people.
- Every AI suggestion and every human approval appends to `audit_log`.
