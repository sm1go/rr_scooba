// Small synthetic fixtures used only when the API is not reachable.
// They mirror db/seed (recorded demo world) so the story is the same online and offline.
import type {
  Band,
  ChallengeCard,
  Company,
  CompanySparks,
  DraftResponse,
  EventInfo,
  LintHint,
  Meeting,
  MeetingSheet,
  Pool,
} from '../types'

export const SAMPLE_AD = `Lumo Systems Oy is hiring a backend developer!
We are a young and dynamic team of 14 in Otaniemi, Espoo, building the booking platform Finnish tradespeople rely on.

You will fit right in if you have:
- fluent Finnish (our customers call in Finnish)
- Master's degree required in Computer Science or similar
- solid Python experience and a habit of automated testing
- no unexplained gaps in your CV

The real problem waiting for you: our CI pipeline takes 40 minutes for every merge and it is eating the team's day. In your first 90 days you make it fast again.
Photo on the CV appreciated. Apply now!`

export const eventInfo: EventInfo = {
  id: 'ev-2026-11',
  name: 'TalentMatch Espoo · Tech & ICT',
  date: '2026-11-26',
  format: 'hybrid',
  companies_declared: 40,
  talents_registered_band: '50+',
}

export const lumo: Company = {
  id: 'co-lumo',
  name: 'Lumo Systems Oy',
  size: 14,
  city: 'Espoo',
  contact_name: 'Sanna Virtanen',
  slots: 6,
}

const lumoMustHaves = (prefix: string) => [
  {
    id: `${prefix}1`,
    text: 'Has made a slow build or CI pipeline measurably faster',
    how_we_check: 'Walk us through one pipeline you sped up — what you changed and the before/after numbers',
    esco_label: 'use continuous integration and delivery tools',
  },
  {
    id: `${prefix}2`,
    text: 'Builds backend services in Python',
    how_we_check: 'Show and explain a Python service you wrote yourself',
    esco_label: 'develop software in Python',
  },
  {
    id: `${prefix}3`,
    text: 'Writes automated tests as part of daily work',
    how_we_check: 'Describe a test that caught a real bug before release',
    esco_label: 'develop automated software tests',
  },
]

export const draftCard: ChallengeCard = {
  id: 'card-co-lumo-draft',
  company_id: 'co-lumo',
  title: 'Backend developer — make our CI fast again',
  problem_90d: 'Our CI pipeline takes 40 minutes for every merge. Releases slip and senior developers burn review time waiting on builds.',
  must_haves: lumoMustHaves('reqd-lumo-'),
  nice_to_haves: ['A fit for our young and dynamic team', "Master's degree required"],
  languages: [{ language: 'Finnish', level: 'C2', task: '', from_when: 'day one' }],
  work_mode: 'hybrid — Otaniemi office, 2 days on site',
  status: 'draft',
  company_minutes_spent: 0,
}

const LAW = 'Non-Discrimination Act 1325/2014'

const WORD_RULES: { rule: string; words: string[]; why: string; law?: string; suggestion: string }[] = [
  {
    rule: 'native_speaker',
    words: ['native speaker', 'mother tongue'],
    why: 'Being a native speaker is not a skill. Describe the language task instead.',
    law: LAW,
    suggestion: "Name the task, e.g. 'Finnish B2 for written customer reports'",
  },
  {
    rule: 'age_words',
    words: ['young', 'digital native'],
    why: 'Age-coded words signal preference for a certain age group, which the law treats as discrimination.',
    law: LAW,
    suggestion: "Describe the team by what it does, not its age — e.g. 'a small team that ships weekly'.",
  },
  {
    rule: 'degree_without_reason',
    words: ["master's", 'degree'],
    why: 'A degree requirement without a stated reason shrinks the pool where the degree is not needed for the task.',
    law: LAW,
    suggestion: "Name the skill the degree was meant to prove — e.g. 'can design a database schema' — and check that instead.",
  },
  {
    rule: 'cultural_fit',
    words: ['cultural fit'],
    why: '"Cultural fit" is vague and often hides bias. Name the behaviour you need.',
    suggestion: "Name the behaviour — e.g. 'gives and takes code review feedback openly'.",
  },
]

/** Offline lint: tiny copy of the server rulebook so the editor still teaches. */
export function offlineLint(card: ChallengeCard): LintHint[] {
  const hints: LintHint[] = []
  for (const l of card.languages) {
    if ((l.level === 'C1' || l.level === 'C2') && !l.task.trim()) {
      hints.push({
        id: `hint-lang-${l.language}`,
        rule: 'language_proxy',
        trigger: `${l.language} ${l.level} with no stated task`,
        why: 'Asking for native-level language without naming the task screens out capable international talent and can mask origin-based discrimination.',
        law: LAW,
        suggestion: 'Keep the team English-speaking; set Finnish at B1 for customer calls by month 6 (course paid).',
        pool_before: 'fewer than 10',
        pool_after: '20–49',
      })
    }
  }
  const texts: { text: string; requirement_id?: string }[] = [
    ...card.must_haves.flatMap((r) => [
      { text: r.text, requirement_id: r.id },
      { text: r.how_we_check, requirement_id: r.id },
    ]),
    ...card.nice_to_haves.map((t) => ({ text: t })),
    { text: card.title },
    { text: card.problem_90d },
  ]
  for (const r of WORD_RULES) {
    for (const t of texts) {
      const w = r.words.find((x) => t.text.toLowerCase().includes(x))
      if (w) {
        hints.push({
          id: `hint-${r.rule}`,
          rule: r.rule,
          trigger: w,
          requirement_id: t.requirement_id,
          why: r.why,
          law: r.law,
          suggestion: r.suggestion,
          pool_before: 'fewer than 10',
          pool_after: 'fewer than 10',
        })
        break
      }
    }
  }
  return hints.slice(0, 5)
}

/** Offline pool: bands only. The language need is what moves the band in the demo. */
export function offlinePool(card: ChallengeCard): Pool {
  const strict = card.languages.some((l) => l.language.toLowerCase() === 'finnish' && ['B2', 'C1', 'C2'].includes(l.level))
  const band: Band = strict ? 'fewer than 10' : '20–49'
  return {
    band,
    elasticity: card.must_haves.map((r, i) => ({
      requirement_id: r.id,
      text: r.text,
      band_without: (strict ? (i === 0 ? '10–19' : 'fewer than 10') : '50+') as Band,
    })),
  }
}

export const draftResponse: DraftResponse = {
  card: draftCard,
  followups: [
    'Is Finnish needed for customer calls or only internal chat — and by when?',
    'Which pipeline is the slow one — build, test or deploy?',
    "Is the Master's degree about a specific skill we should name instead?",
  ],
  lint: offlineLint(draftCard),
  pool: offlinePool(draftCard),
  trace: [
    { tool: 'esco_search', input: {}, output_summary: '3 skills: use continuous integration and delivery tools, develop software in Python, develop automated software tests', ms: 1 },
    { tool: 'lint_requirements', input: {}, output_summary: '3 results', ms: 17 },
    { tool: 'pool_preview', input: {}, output_summary: 'pool band: fewer than 10', ms: 12 },
    { tool: 'submit_card', input: {}, output_summary: 'stored card card-co-lumo-draft (status draft)', ms: 3 },
  ],
  provider: 'mock',
}

export const approvedCards: ChallengeCard[] = [
  {
    ...draftCard,
    id: 'card-co-lumo',
    must_haves: lumoMustHaves('req-lumo-r'),
    nice_to_haves: ['Interest in mentoring juniors'],
    languages: [
      { language: 'Finnish', level: 'B1', task: 'customer calls', from_when: 'by month 6' },
      { language: 'English', level: 'B2', task: 'daily team work', from_when: 'from day one' },
    ],
    status: 'approved',
    company_minutes_spent: 9,
  },
  {
    id: 'card-co-aurora',
    company_id: 'co-aurora',
    title: 'ML engineer — triage assistant',
    problem_90d: 'Our triage model works in a notebook but has never been deployed.',
    must_haves: [
      { id: 'req-co-aurora-r1', text: 'Has deployed a machine learning model', how_we_check: 'Walk us through a concrete example from your own work' },
      { id: 'req-co-aurora-r2', text: 'Builds software in Python', how_we_check: 'Show us something you built and explain your part in it' },
      { id: 'req-co-aurora-r3', text: 'Sets up monitoring or alerts', how_we_check: 'Tell us about an alert that caught a real problem' },
    ],
    nice_to_haves: [],
    languages: [{ language: 'English', level: 'B2', task: 'team meetings', from_when: 'from day one' }],
    work_mode: 'remote-first, Espoo',
    status: 'approved',
    company_minutes_spent: 7,
  },
]

const claimBuild = {
  id: 'cl-amira-build',
  text: 'I helped cut our build time from 30 to 6 minutes',
  quote: 'I helped cut our build time from 30 to 6 minutes',
  esco_label: 'use continuous integration and delivery tools',
  evidence_level: 'own words' as const,
  confirmed: true,
}

export const companySparks: CompanySparks = {
  minutes_estimate: 6,
  by_requirement: [
    {
      requirement: approvedCards[0].must_haves[0],
      sparks: [
        { id: 'sp-local-1', pseudonym: 'Talent #0427', claim: claimBuild, note: 'Your 40-minute pipeline sounds like the one I fixed.', status: 'sent', deadline: '2026-11-20T16:00:00+02:00' },
        {
          id: 'sp-local-2',
          pseudonym: 'Talent #0193',
          claim: { ...claimBuild, id: 'cl-0193-1', text: 'Split the test suite to run in parallel', quote: 'we split the test suite so it ran in parallel on four machines', evidence_level: 'artefact' },
          status: 'sent',
          deadline: '2026-11-20T16:00:00+02:00',
        },
      ],
    },
    {
      requirement: approvedCards[0].must_haves[1],
      sparks: [
        {
          id: 'sp-local-3',
          pseudonym: 'Talent #0211',
          claim: { ...claimBuild, id: 'cl-0211-1', text: 'Maintained a Python booking service', quote: 'I maintained the Python service that handled bookings for two years', esco_label: 'develop software in Python' },
          status: 'sent',
          deadline: '2026-11-21T16:00:00+02:00',
        },
      ],
    },
    { requirement: approvedCards[0].must_haves[2], sparks: [] },
  ],
}

export const meetings: Meeting[] = [
  { id: 'mt-001', spark_id: 'sp-008', talent_name: 'Mei Kimura', slot: 'Thu 26 Nov · 10:00', card_id: 'card-co-lumo' },
  { id: 'mt-002', spark_id: 'sp-009', talent_name: 'Tomas Okafor', slot: 'Thu 26 Nov · 10:20', card_id: 'card-co-lumo' },
]

export const meetingSheet: MeetingSheet = {
  meeting_id: 'mt-001',
  questions: approvedCards[0].must_haves.map((r) => ({ requirement_id: r.id, question: r.text, how_we_check: r.how_we_check })),
  ticks: approvedCards[0].must_haves.map((r) => ({ requirement_id: r.id, seen: false })),
}
