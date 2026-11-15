export interface Condition {
  key: string
  value: 'yes' | 'no' | 'unknown'
  source: 'employer' | 'advisor' | null
  checked_at: string | null
  note: string
}

export interface JobLabel {
  id: string
  why: string
}

export interface Shift {
  day: string
  start: string
  end: string
}

export interface LanguageNeed {
  language: string
  level: string
  task: string
}

export interface Job {
  id: string
  employer_id: string
  title: string
  field: string
  duties: string[]
  address: string
  district: string
  lat: number | null
  lon: number | null
  work_mode: 'on_site' | 'hybrid' | 'remote'
  pay_amount: number | null
  pay_unit: 'hour' | 'month' | null
  pay_note: string
  shifts: Shift[]
  schedule_flexible: boolean
  break_min: number
  rota: boolean
  hours_min: number | null
  hours_max: number | null
  contract: string | null
  experience: 'none' | 'some' | 'required' | null
  experience_note: string
  qualifications: string[]
  onboarding: string
  languages: LanguageNeed[]
  lifting: string | null
  apply_question: string
  cv_required: boolean
  commitments: string[]
  contract_id: string | null
  city_contract: { id: string; title: string; due: string } | null
  positions: number
  status: 'draft' | 'open' | 'closed'
  source: 'employer' | 'advisor'
  confirmed_at: string | null
  employer: { id: string; name: string } | null
  labels: JobLabel[]
  conditions: Condition[]
  event: { name: string; date: string; venue: string; booth: string } | null
  confirmed_days_ago: number | null
  stale: boolean
  distance_km?: number
  applications_count?: number
  nearest_station: { name: string; mode: 'metro' | 'train'; distance_m: number } | null
  commute?: Commute | null
}

export interface Commute {
  minutes: number
  walk_m: number
  transfers: number
  legs: { mode: string; route: string | null; from: string; to: string; minutes: number }[]
  arrive_by: string
  date: string
  source: string
}

export interface Catalog {
  fields: { id: string; name: string }[]
  districts: { id: string; name: string; lat: number; lon: number }[]
  condition_keys: { id: string; label: string }[]
  contract_types: string[]
  language_levels: string[]
  labels: { id: string; name: string }[]
  availability_parts: { id: string; hours: string }[]
  employers: { id: string; name: string }[]
}

export interface User {
  id: string
  email: string | null
  phone: string | null
  role: 'resident' | 'employer' | 'advisor'
  name: string
  employer_id?: string
  employer_name?: string
}

export interface Profile {
  contact_method: 'phone' | 'sms' | 'email' | null
  district: string | null
  fields: string[]
  availability: string[]
  max_hours_per_week: number | null
  needs: string[]
  languages: { language: string; level: string }[]
  about: string
  name: string
  email: string | null
  phone: string | null
  share_email: boolean
  share_phone: boolean
  public_link: string
}

export interface Application {
  id: string
  job_id: string
  name: string
  contact_method: string
  contact_value: string
  availability_note: string
  answer: string
  shared_needs: string[]
  meet_at_event: boolean
  meets_must_haves: boolean
  wants_tryout: boolean
  queue_position: number | null
  contract_eligible: boolean
  shared_credentials: { label: string; checked_at: string }[]
  shared_event_records: EventRecord[]
  status: 'sent' | 'interview' | 'offer' | 'not_selected' | 'withdrawn' | 'job_closed'
  status_note: string
  created_by_advisor: boolean
  created_at: string
  updated_at: string
  days_waiting: number
  job?: { id: string; title: string; status: string;
          employer_name: string; commitments?: string[] }
  history?: { action: string; detail: string; created_at: string }[]
}

export interface HelpRequest {
  id: string
  user_id: string | null
  name: string
  contact_method: string
  contact_value: string
  job_id: string | null
  kind: 'check_conditions' | 'prepare_application' | 'arrange_contact' | 'other' | 'employer_support' | 'check_document'
  condition_keys: string[]
  document_label?: string
  message: string
  status: 'new' | 'in_progress' | 'done'
  advisor_reply: string
  created_at: string
  job?: {
    id: string; title: string; employer_name: string
    employer_contact_name?: string
    employer_contact_email?: string
    employer_contact_phone?: string
  }
}

export interface WordingTip {
  id: string
  rule: string
  field: string
  trigger: string
  why: string
  suggestion: string
}

export interface EmployerProfile {
  id: string
  name: string
  about: string
  contact_name: string
  contact_email: string
  contact_phone: string
  share_email: boolean
  share_phone: boolean
  public_link: string
  badges: { id: string; kind: string; label: string; note: string }[]
  event: { name: string; date: string; venue: string; booth: string } | null
}

export interface Overview {
  open_jobs: number
  stale_jobs: { id: string; title: string; employer_name: string; confirmed_days_ago: number }[]
  waiting_over_7_days: {
    id: string; job_id: string; job_title: string; applicant_name: string
    status: string; days_waiting: number
    employer: { name: string; contact_email: string; contact_phone: string } | null
  }[]
  new_help_requests: number
  applications_by_status: Record<string, number>
  event_talks_unanswered: {
    id: string
    person_name: string
    employer_name: string
    days_waiting: number
    employer: { name: string; contact_name: string; contact_email: string; contact_phone: string }
  }[]
}

export interface EventTalk {
  id: string
  event_id: string
  user_id: string
  employer_id: string
  status: 'talked' | 'answered'
  outcome: 'next_step' | 'not_now' | null
  employer_note: string
  talked_at: string
  answered_at: string | null
  next_kind?: 'interview' | 'tryout' | 'call' | null
  next_at?: string | null
  next_place?: string | null
  simulated?: boolean
  employer_name?: string
  person_name?: string
  person_contact_method?: string
  person_contact_value?: string
  days_waiting?: number
  employer?: { name: string; contact_name: string; contact_email: string; contact_phone: string } | null
}

export interface EventInfo {
  event: { id: string; name: string; date: string; venue: string; advisor_note: string } | null
  employers: { id: string; name: string; booth: string; tagline?: string
    field?: string; logo_color?: string
    jobs: { id: string; title: string }[] }[]
}

export interface EventPlan {
  event: EventInfo['event']
  code: string | null
  booths: { employer_id: string; name: string; booth: string; jobs: { id: string; title: string }[] }[]
}

export interface CompanyProfile {
  id: string; name: string; about: string; tagline: string
  field: string; district: string; address: string
  size_band: string; founded: number | null
  work_languages: string[]; logo_color: string; how_we_welcome: string
  contact_name: string; contact_email: string; contact_phone: string
  jobs: Job[]; contracts: string[]
  badges: { kind: string; label: string; event_name: string }[]
  events: { event_id: string; name: string; date: string
            booth: string | null; past: boolean
            need_card: NeedCard | null }[]
  commitments: string[]
}

export interface EventAfterData {
  summaries: {
    event_id: string; name: string; date: string
    employers: number; participants: number; talks: number
    answered: number; answered_in_7d_pct: number | null
    next_steps: number; hired: number
  }[]
  mine: {
    event_id: string; name: string; date: string
    talks: { employer: string; outcome: string | null
             note: string; answered: boolean }[]
    records: { employer: string; date: string; observed: string[] }[]
    badges: { id: string; kind: string; label: string; event_id: string
              note: string; event_name: string }[]
    people: { user_id: string; name: string; role: string
              company: string | null }[]
  }[]
}

export interface EmployerEvent {
  event: EventInfo['event']
  booth: string | null
  visitors_planned: number
  talks: EventTalk[]
}

export interface SupportProgram {
  id: string
  name: string
  amount: string
  for_employer: string | null
  for_resident: string | null
  paid_to: 'employer' | 'resident' | 'nobody'
  resident_when_all: string[]
  resident_when_any: string[]
  job_rule: string | null
  source_name: string
  source_url: string
}

export interface SupportCatalogue {
  meta: { checked_on: string; disclaimer: string; note?: string }
  situations: { id: string; label: string }[]
  programs: SupportProgram[]
}

export interface FiltersReply {
  filters: Record<string, unknown>
  explanation: string[]
  not_understood: string[]
  source: 'ai' | 'rules'
}

export interface JobDraft {
  draft: Record<string, unknown>
  missing: string[]
  wording_warnings: string[]
  source_quotes: Record<string, string>
}

export interface CallScript {
  opening: string
  questions: { field: string; question: string }[]
  kinds?: Record<string, string>
  employer?: { name: string; contact_name: string; contact_email: string; contact_phone: string } | null
  source: 'ai' | 'rules'
}

export interface AdvisorNote {
  type: 'help_request' | 'application' | 'job_conditions'
  person_name: string | null
  contact_method: 'phone' | 'sms' | 'email' | null
  contact_value: string | null
  job_hint: string | null
  kind: string | null
  message: string | null
  availability_note: string | null
  answer: string | null
  needs: string[]
  conditions: { key: string; value: 'yes' | 'no'; note: string }[]
  consent_mentioned: boolean
  left_out: string[]
}

export interface SimplerSections {
  title: string | null
  duties: string[] | null
  experience_note: string | null
  qualifications: string[] | null
  onboarding: string | null
  pay_note: string | null
  lifting: string | null
  apply_question: string | null
  language_tasks: string[] | null
}

export const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as const
export const PARTS = ['morning', 'afternoon', 'evening'] as const
export const CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const

export interface Bundle {
  jobs: Job[]
  hours_min: number
  hours_max: number
  max_km_apart: number
  week: Record<string, { job_id: string; start: string; end: string }[]>
  pay_week_eur: number | null
}

export interface CityContract {
  id: string; title: string; due: string
  starts?: string; ends?: string; value_eur?: number
  hires_required: number; hires_done: number
  status?: 'done' | 'behind' | 'on_track'; open_jobs?: number
  target_groups?: string[]
  employer?: { id: string; name: string; contact_name: string;
               contact_phone: string; contact_email: string }
}

export interface Credential {
  id: string; label: string; checked_at: string; advisor_id: string
}

// --- v9 event-centred model -------------------------------------------------
export interface EventSummary {
  id: string; name: string; date: string; format: string; language: string
  starts_at: string; ends_at: string; venue: string; address: string
  description: string; capacity: number; slot_minutes: number
  need_deadline: string; publish_date: string; phase: string
  registration_opens?: string; matching_closes?: string
  answers_due?: string; series?: string
  employer_count: number; registered: number
  programme: { kind: string; start: string; end?: string; title?: string }[]
  time_groups: { id: string; label?: string; entry: string }[]
}
export interface DoneItem { text: string; own_words?: string }
export interface TalentCardData {
  done: DoneItem[]; looking_for: string; district: string
  availability: string[]
}
export interface NeedCard {
  first_week: string[]
  must_haves: { text: string; why: string }[]
  will_teach: string[]
  languages: { name: string; level: string; task: string }[]
  job_ids: string[]
}
export interface NeedEntry {
  employer_id: string; employer_name?: string; booth: string | null
  slots: number; formats: string[]
  tagline?: string; field?: string; logo_color?: string; open_jobs?: number
  need: { card: NeedCard; submitted_at: string; need_by: string } | null
  fit?: { key: string; [k: string]: unknown }[]
  interested?: boolean; meets?: number[]
  language_levels?: Record<string, string>
  company_badges?: string[]
}
export interface EventDetailData extends EventSummary {
  employers: NeedEntry[]; needs_published: boolean
}
export interface MyRegistration {
  id: string; event_id: string; time_group: string; status: string
  card_language: string; card: TalentCardData; created_at: string
}
export interface MyMeeting {
  id: string; employer_id: string; employer_name: string
  booth: string | null; starts_at: string; status: string
  need_line?: string; video_url?: string | null
  first_week?: string[]; must_haves?: string[]; bring?: string[]
}
export interface MyEventInterest {
  employer_id: string; name: string; meets: number[]
  language_levels: Record<string, string>
}
export interface MyEventData {
  event: EventSummary
  registration: MyRegistration | null
  interests: MyEventInterest[]
  meetings: MyMeeting[]
  talks: { id: string; employer_id: string; employer_name: string;
           status: string; outcome: string | null; note: string | null
           observed?: string[]; talked_at?: string | null
           answered_at?: string | null
           next_kind?: 'interview' | 'tryout' | 'call' | null
           next_at?: string | null; next_place?: string | null
           talent_response?: 'confirmed' | 'other_time' | null
           talent_response_note?: string | null
           simulated?: boolean }[]
  visitor_code: string | null
  interest_limit: number
  queue: { employer_id: string; status: string; joined_at: string;
           employer_name: string }[]
  entry: string | null
}
export interface AnonTalentCard {
  id: string; looking_for: string
  done: DoneItem[]; meets: number[]
  language_levels: Record<string, string>; availability: string[]
  district: string; credentials: string[]; time_group: string
  interested: boolean; invited: boolean; invited_at?: string | null
  fit?: { key: string; [k: string]: unknown }[]
  kudos?: { label: string; count: number }[]
}
export interface EmployerWorkspace {
  event: EventSummary; joined: boolean; booth?: string
  slots?: number; formats?: string[]
  need?: { card: NeedCard; submitted_at: string; need_by: string } | null
  invites_used?: number
  meetings?: { id: string; starts_at: string; status: string;
               video_url?: string | null }[]
  talks?: EventTalk[]
}
export interface EmployerDay {
  event: EventSummary; booth: string | null
  meetings: { id: string; user_id: string; starts_at: string;
              status: string }[]
  next_card: (AnonTalentCard & { meeting_id: string }) | null
  queue: { user_id: string; status: string; joined_at: string;
           registration_id: string }[]
}
export interface OrganizerDay {
  event: EventSummary
  booths: { employer_id: string; name: string; booth: string | null
            now: string | null; next: string | null
            done: number; no_show: number; free_slots: number;
            queue: number }[]
}
export interface OrganizerReport {
  event: EventSummary
  booths: { employer_id: string; name: string; booth: string | null
            booked: number; held: number; no_show: number;
            next_step: number }[]
  need_cards_on_time_pct: number | null
  answers_in_7d_pct: number | null
  fairness: { card_language: string; registered: number; chose: number
              invited: number; met: number; next_step: number
              rates: Record<string, number> | null }[]
}
export interface EventRecord {
  employer: string; date: string; observed: string[]
}
export interface AdvisorBoard {
  event: EventSummary
  employers: {
    employer_id: string; name: string; booth: string | null; slots: number
    need_status: string; need_submitted_at: string | null
    need_by: string | null; reminders_sent: number
    days_to_deadline: number | null
    contact_name: string | null; contact_email: string | null
    contact_phone: string | null
    invites_used: number; meetings: number
  }[]
  talent: { by_time_group: Record<string, number>; waitlist: number;
            mutual_matches: number; meetings: number }
}

export interface Connection {
  user_id: string; name: string; role: string
  company: string | null; event_id: string; event_name: string
  connected_at: string; my_note: string
  email?: string; phone?: string; public_link?: string
}
export interface MyBadge {
  id: string; kind: string; label: string; note: string
  hidden: boolean; created_at: string
  event_name: string; event_id: string; giver_name: string | null
}

// §9.7 online event: virtual booth Q&A + networking lounge
export interface EventQuestion {
  id: string; employer_id: string; asked_by: string; user_id: string
  text: string; answer: string | null; answered_by: string | null
  created_at: string; answered_at: string | null
}
export interface BoothData {
  event_id: string; employer_id: string; name: string
  tagline?: string; field?: string; logo_color?: string
  booth: string | null; need_item: NeedEntry | null
  open_jobs: Job[]; questions: EventQuestion[]
  can_ask: boolean; can_answer: boolean
}
export interface LoungeMember {
  user_id: string; first_name: string; looking_for: string; done: string
  joined_at: string; connected: boolean
}
export interface LoungeData {
  event_id: string; joined: boolean; members: LoungeMember[]
}
