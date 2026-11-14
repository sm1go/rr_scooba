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
  status: 'sent' | 'interview' | 'offer' | 'not_selected' | 'withdrawn' | 'job_closed'
  status_note: string
  created_by_advisor: boolean
  created_at: string
  updated_at: string
  days_waiting: number
  job?: { id: string; title: string; status: string; employer_name: string }
  history?: { action: string; detail: string; created_at: string }[]
}

export interface HelpRequest {
  id: string
  user_id: string | null
  name: string
  contact_method: string
  contact_value: string
  job_id: string | null
  kind: 'check_conditions' | 'prepare_application' | 'arrange_contact' | 'other'
  condition_keys: string[]
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
}

export const DAYS = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] as const
export const PARTS = ['morning', 'afternoon', 'evening'] as const
export const CEFR = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2'] as const
