# App v2 spec — "Espoo Work Map"

Status: accepted (owner, 14 Nov). Replaces the v1 role-switcher demo, which is preserved
as git tag `demo-v1`. v1 code (Sparks, Challenge Cards, evidence claims, pool bands, LLM
adapter, organiser trust lab, offline fixtures) is **removed** from `main`; do not keep
dead code. Keep and adapt only: the SQLite/seed/audit plumbing in `app/api/db.py`, the
wording rules in `app/api/rules/lint.py`, the event seed, and the test conventions.

## 1. Concept

A city map and list of concrete jobs in Espoo, with a city employment advisor one tap
away. People find a job by duties, hours, pay, place and working conditions, and get in
touch in a minute — alone or with an advisor. Every job can lead to a conversation at the
next City of Espoo recruitment event, and every contact is followed until it has an answer.

Audiences (never assumed, always self-selected): people with disabilities, students and
young people looking for a first or side job, retirees who want some extra work,
international residents, and anyone using the city's employment services. Jobs span
cleaning, retail, restaurants, care, logistics, office, customer service, seasonal work
and specialist roles. Employers and advisors are non-technical too.

Rules that do not bend:
- No scores, no ranking of people, no automatic rejection, no AI in v2.
- Labels and filters describe **the job's conditions**. A label means "fits", never
  "only for"; anyone may apply. Employers cannot enter an age requirement.
- A person states what they need, never a diagnosis, and chooses per application what
  the employer is told.
- Missing information is shown as "Not known yet" — never guessed.
- Synthetic data only. Minimal personal data. Home address is never collected.
- No candidate map, no pitches, quizzes, portfolios or gamification.

## 2. Data model (SQLite, `db/schema.sql`; bump `PRAGMA user_version` and rebuild an
older on-disk DB from schema + seed)

```
user(id, email UNIQUE NULL, phone NULL, password_hash, role CHECK IN
     ('resident','employer','advisor'), name, employer_id NULL, created_at)
session(token PK, user_id, created_at)
resident_profile(user_id PK, contact_method CHECK IN ('phone','sms','email'),
     district, fields JSON, availability JSON, max_hours_per_week INT NULL,
     needs JSON, languages JSON, about TEXT)
employer(id, name, about, contact_name, contact_email, contact_phone)
event(id, name, date, venue, advisor_note)                 -- keep the seeded event
employer_event(employer_id, event_id, booth)
job(id, employer_id, title, field, duties JSON[str], address, district, lat, lon,
    work_mode CHECK IN ('on_site','hybrid','remote'),
    pay_amount REAL NULL, pay_unit CHECK IN ('hour','month') NULL, pay_note,
    shifts JSON [{day:'mon'..'sun', start:'18:00', end:'21:00'}],
    schedule_flexible INT, hours_min INT NULL, hours_max INT NULL,
    contract CHECK IN ('permanent','fixed_term','seasonal','gig','summer_job','traineeship'),
    experience CHECK IN ('none','some','required'), experience_note,
    qualifications JSON[str], onboarding, languages JSON [{language, level, task}],
    lifting TEXT NULL, apply_question, cv_required INT DEFAULT 0,
    positions INT, status CHECK IN ('draft','open','closed'),
    source CHECK IN ('employer','advisor'), confirmed_at DATE, created_at)
job_condition(job_id, key, value CHECK IN ('yes','no'), source CHECK IN
    ('employer','advisor'), checked_at DATE, note, PRIMARY KEY(job_id,key))
    -- no row = "Not known yet"
saved_job(user_id, job_id)
application(id, job_id, user_id NULL, name, contact_method, contact_value,
    availability_note, answer, cv_text NULL, shared_needs JSON, meet_at_event INT,
    status CHECK IN ('sent','interview','offer','not_selected','withdrawn','job_closed'),
    status_note, created_by_advisor INT, created_at, updated_at)
help_request(id, user_id NULL, name, contact_method, contact_value, job_id NULL,
    kind CHECK IN ('check_conditions','prepare_application','arrange_contact','other'),
    condition_keys JSON, message, consent INT, status CHECK IN ('new','in_progress','done'),
    advisor_id NULL, advisor_reply, created_at, updated_at)
audit_log (as now)
```

Condition keys (shared vocabulary, served by `/api/catalog` with plain labels):
`step_free_entrance`, `lift`, `accessible_toilet`, `seated_work`, `flexible_breaks`,
`quiet_environment`, `written_instructions`, `sign_language_ok`,
`assistive_tech_ok`, `adjustments_negotiable`. Physical load is the free text `lifting`
("Up to 10 kg, a few times per shift"; NULL = not known yet).

Availability JSON = list of slots `"<day>-<part>"`, day `mon..sun`, part
`morning` (06–12) / `afternoon` (12–17) / `evening` (17–23).

### Derived labels (computed server-side in `app/api/rules/labels.py`, returned as
`labels: [...]` on every job; each label carries `why`, a plain sentence)

| id | UI label | Rule |
|---|---|---|
| `students` | Fits students | `hours_max ≤ 25` and (`schedule_flexible` or every shift starts ≥ 16:00 or is on sat/sun) |
| `retirement` | Extra work in retirement | `hours_max ≤ 20` and (`schedule_flexible` or at least one shift ends ≤ 18:00) |
| `first_job` | First job / no experience | `experience = 'none'` and `onboarding` not empty |
| `side_job` | Side job | `hours_max ≤ 20` |
| `part_time` | Part-time | `hours_max < 30` |
| `access_info` | Access details given | at least 4 condition keys have a row |

Unknown hours (`hours_max` NULL) never produce a label. A job fits a set of availability
slots when every shift lies inside a selected slot, or `schedule_flexible` is true.

## 3. API (FastAPI). Auth: `Authorization: Bearer`, scrypt hashes, `secrets.token_urlsafe`.

Public (no account):
- `GET /api/catalog` → fields, condition keys+labels, label ids, districts
  `[{id,name,lat,lon}]` (Leppävaara, Tapiola, Otaniemi, Matinkylä, Olari, Niittykumpu,
  Espoon keskus, Espoonlahti, Kauklahti, Kalajärvi), contract types, language levels.
- `GET /api/jobs` — open jobs. Query filters, all optional and combinable: `label`
  (repeatable), `field`, `slots` (comma list, availability fit), `hours_max`, `pay_min`
  (+`pay_unit`), `contract`, `experience`, `work_mode`, `language` + `level_max` (jobs
  whose need for that language is at or below the level, or that do not need it),
  `needs` (comma list of condition keys: keep jobs where each is `yes`; with
  `needs_mode=not_no` keep jobs where none is `no`), `district` + `km` (haversine from
  the district centre; remote jobs always pass), `at_event=1`, `q` (title/duties/employer).
  Order: `confirmed_at` descending, then title. Never ordered by person.
  Each item: all job fields, `employer: {id,name}`, `labels`, `conditions`
  (all 10 keys, each `{key, value:'yes'|'no'|'unknown', source, checked_at, note}`),
  `event: {name,date,venue,booth} | null`, `confirmed_days_ago`, `stale` (true when
  `confirmed_at` is older than 14 days), `distance_km` when `district` was given.
- `GET /api/jobs/{id}` → same shape (open jobs; drafts/closed only for the owner/advisor).
- `GET /api/event` → next event + participating employers.
- `POST /api/auth/register` `{role:'resident'|'employer', name, email?, phone?, password,
  employer_name?}` (one of email/phone required; advisors cannot register),
  `POST /api/auth/login` `{login, password}` (login = email or phone),
  `POST /api/auth/logout`, `GET /api/me`.

Resident:
- `GET/PUT /api/me/profile`; `GET /api/me/export`; `DELETE /api/me` (removes profile,
  saved jobs, sessions; applications and help requests are anonymised: `user_id` NULL,
  name "Deleted user", contact and answer emptied).
- `GET /api/me/saved`, `PUT/DELETE /api/me/saved/{job_id}`.
- `POST /api/applications` `{job_id, contact_method, contact_value, availability_note,
  answer, cv_text?, shared_needs: [keys], meet_at_event}`. 422 if `answer` is empty or
  `cv_required` and no `cv_text`; 409 if the person already applied to this job, if the
  job is not open, or if they have **5 active** applications (`sent`/`interview`) —
  message: "You have 5 open applications. Withdraw one or wait for an answer."
- `GET /api/me/applications` (with job summary, status, status_note, history of status
  changes from the audit log), `POST /api/applications/{id}/withdraw`.
- `POST /api/help-requests` (also allowed **without an account**: then `name` and
  contact are required) `{job_id?, kind, condition_keys, message, consent, name?,
  contact_method, contact_value}`; `consent` must be true (422 otherwise).
  `GET /api/me/help-requests`.

Employer (only own data, 403 otherwise):
- `GET/PUT /api/employer` (profile), `GET /api/employer/jobs`, `POST /api/jobs`,
  `PUT /api/jobs/{id}`, `POST /api/jobs/{id}/confirm` (sets `confirmed_at` = today),
  `POST /api/jobs/{id}/close` (open applications → `job_closed`),
  `POST /api/jobs/{id}/publish`.
- Job conditions are written through the job payload as `{key: 'yes'|'no'|'unknown'}`
  with source `employer`; an employer write never overwrites a row whose source is
  `advisor` unless the value changes (then source becomes `employer` again).
- `POST /api/jobs/check-wording` `{text fields}` → tips from the adapted lint rules
  (age, "native" language, gender, health, nationality wording; language level without
  a task). Advisory only. Publishing is blocked (422) only when an age or other
  protected-ground requirement is stated in `experience_note`/`qualifications`.
- `GET /api/employer/applications?job_id=` — name, contact, availability note, answer,
  `shared_needs` (only the keys the applicant chose), `meet_at_event`, status.
  `POST /api/applications/{id}/status` `{status:'interview'|'offer'|'not_selected',
  status_note}`; `status_note` is required (interview: when and where; not_selected: a
  short human-written reason). No bulk actions.

Advisor (seeded account only):
- `GET /api/advisor/help-requests?status=`, `POST /api/advisor/help-requests/{id}`
  `{status, advisor_reply}` (assigns the advisor).
- `PUT /api/advisor/jobs/{id}/conditions` `{key, value:'yes'|'no', note}` → source
  `advisor`, `checked_at` today, audit `condition_checked`.
- `POST /api/jobs`, `PUT /api/jobs/{id}` for any employer (`source='advisor'`), plus
  `POST /api/advisor/employers` to add an employer without an account.
- `POST /api/advisor/applications` — apply on behalf of a walk-in or phone caller
  (`name`, contact, answer…, `consent: true` required, `created_by_advisor=1`,
  `user_id` optional).
- `GET /api/advisor/overview` — counts: open jobs, stale jobs, applications waiting
  more than 7 days for an answer (list with employer contact), new help requests,
  applications by status. `GET /api/audit`.
- An advisor sees a resident's profile needs **only** through what the resident put in a
  help request or application. There is no "browse residents" endpoint.

Privacy tests that must exist: `needs` from the profile never appear in any employer or
advisor response; `shared_needs` appear to the employer only for that application; the
jobs API output is identical for anonymous and signed-in callers; no endpoint returns
keys named score/rank/rating.

## 4. Seed (`scripts/generate_synthetic.py`, deterministic; regenerate `db/seed/*.json`)

- 60 open jobs from ~28 employers spread over real Espoo districts with plausible
  coordinates and street addresses; fields: cleaning, retail, restaurant, care,
  logistics, office, customer service, education, construction, tech, seasonal.
  Realistic Finnish pay (roughly 11.5–16 €/h for hourly work; monthly for specialist
  roles), concrete duties (3–5 bullet sentences), shifts, onboarding, language needs
  written as tasks, an `apply_question` tied to the duties.
- Deliberate variety: about a third of jobs have several conditions "Not known yet";
  some have `no` values; ~8 jobs are stale (confirmed 15–30 days ago); 12 employers are
  at the event with booths; a few jobs miss pay ("To be agreed").
- Scenario fixtures (used by tests and the demo accounts, password `demo1234`):
  - `aino@example.com` — student; profile availability evenings + weekends, Otaniemi.
    A café job in Tapiola (Sat–Sun 10–16) and an evening office-cleaning job
    ("Office cleaning, Tue and Thu 18:00–21:00, no experience needed, training on site")
    must match her slots.
  - `pekka@example.com` — retiree; two weekday mornings, max 10 h/week, Matinkylä.
    A library-shelving / school-crossing style job with 6–8 h/week must match.
  - `amira@example.com` — needs `step_free_entrance` and `seated_work`; a customer
    service job in Leppävaara has `seated_work: yes (employer)` but
    `step_free_entrance` not known. She has one help request `check_conditions` in
    status `new` for it.
  - `sanna@example.com` — employer (the café), with 3 received applications in
    different statuses. `advisor@example.com` — advisor "Leena, Employment Espoo".

## 5. Frontend (React 19, Vite, TypeScript, Tailwind v4, react-router)

Remove `src/fixtures`, the offline fallback and all v1 pages. Add `leaflet@1.9.4` +
`react-leaflet@5.0.0` (OpenStreetMap tiles, attribution shown; no API key),
`@fontsource-variable/geist`, `@fontsource/hedvig-letters-serif`,
`@fontsource/atkinson-hyperlegible`.

### 5.1 Look — modelled on useminerva.com, enlarged for older and low-vision users

- Warm canvas `#faf9f7`; cards `#ffffff` with 1px hairline `#e8e6e3`, radius 14px, no
  heavy shadows; ink `#171717`; secondary text `#585856` (never lighter).
- Display headings in **Hedvig Letters Serif** (h1 36px, h2 26px, weight 400); body and
  UI in **Geist**; numbers (pay, hours, dates) may use tabular figures.
- Primary button: near-black `#171717`, text `#fbfaf9`, radius 14px. Secondary: white
  with 1.5px `#171717` border. Accent green `#0f7a58` (on `#e3f4ee`) for "yes / checked",
  orange `#b4530b` (on `#fdeedd`) for "not known yet / waiting", red `#b3261e`
  (on `#fdeaea`) for "no / error".
- Status and fact **chips with a coloured dot + words** (never colour alone), like
  Minerva's status column.
- Job list rows like Minerva's tender table but stacked for reading: title (serif,
  22px), employer · district, one line "€13.50 / hour · 6 h / week · Tue, Thu 18–21",
  label chips, "Confirmed 3 days ago" on the right.
- Base font 18px, line-height 1.6, nothing under 16px. Controls min-height 52px, touch
  targets ≥ 48px, visible labels above inputs, focus ring 3px `#171717` + 3px `#ffbf47`.
- Plain words (CEFR A2–B1), no jargon, no emojis, no timers, no auto-dismissing toasts.

### 5.2 Shell

- Top bar: "Espoo Work Map" wordmark, nav, **Accessibility** button, EN / FI switch,
  Sign in or account menu. On phones the nav is a fixed bottom bar, icon + label, max 4.
  - Anyone / resident: Jobs `/`, Saved `/saved`, My applications `/applications`,
    Profile `/profile` (the last three ask to sign in when needed, keeping the return path).
  - Employer: My jobs `/employer`, Applications `/employer/applications`, Company `/employer/company`.
  - Advisor: Requests `/advisor`, Jobs `/advisor/jobs`, Follow-up `/advisor/follow-up`.
- A persistent, quiet "Need help? Ask an advisor" button on resident pages → help form.
- Footer: Accessibility statement, Your data (what is stored, who sees it, download/delete).

### 5.3 Accessibility panel (persisted, applied on `<html>`) — target WCAG 2.2 AA

Text size Normal 18 / Large 21 / Extra large 24 (no breakage at 360px wide); High
contrast (pure black/white, 2px borders, underlined links); Easier reading (Atkinson
Hyperlegible, wider letter/word/line spacing, max 60ch); Reduce motion (and honour
`prefers-reduced-motion`); Listen buttons on/off. Also: skip link, landmarks, one h1 per
page with focus moved to it on navigation, `document.title`, `<html lang>`, full keyboard
operation, `aria-live` for errors and results count ("23 jobs found"), forms keep typed
data on error.

- `ListenButton` — reads a job or page aloud with `speechSynthesis` in the UI language.
- `VoiceInput` — "Speak instead of typing" on every textarea via
  `SpeechRecognition`/`webkitSpeechRecognition`; spoken-language choice (Finnish,
  English, Swedish, Arabic, Ukrainian, Russian, Estonian, Somali); when unsupported show
  "Voice typing works in Chrome or Edge." State once that audio stays in the browser.
- i18n: all UI strings through `t()` with `src/i18n/en.ts` and `src/i18n/fi.ts`
  (clear standard Finnish). Seeded job content stays in English.

### 5.4 Resident screens

- `/` **Jobs** — the home page; no landing page in front of it.
  - Header line: "Jobs in Espoo" + results count + a **List / Map** switch. Wide
    screens: list on the left (scrolls), map on the right (sticky). Phones: list by
    default; Map is the other tab. The list is the full equivalent of the map.
  - Quick filter chips in one row (toggle buttons with `aria-pressed`): Fits students,
    Extra work in retirement, First job / no experience, Side job, Part-time, Access
    details given, At the next event.
  - "More filters" opens a panel (full-screen sheet on phones): **When can you work?**
    as a 7 × 3 grid of large toggles (days × morning/afternoon/evening); hours per week
    (max); pay (min); kind of work; contract; experience; language I can work in +
    my level; on site / hybrid / remote; distance from an area (district + km); **What
    do you need at work?** condition tiles with the choice "Show only jobs where this is
    confirmed" / "Also show jobs where it is not known yet". Signed-in users get
    "Use my profile" to fill these from their profile. "Clear all" always visible.
    Active filters are listed as removable chips. Filters live in the URL query.
  - Map: one marker per on-site/hybrid job (markers are buttons with the job title as
    accessible name); selecting a marker highlights the list row and opens a short card
    (title, employer, pay, hours, Open details). Remote jobs appear only in the list with
    a "Remote" chip. Stale jobs show "Not confirmed recently".
  - Empty result: say which filter removes the most jobs and offer "Ask an advisor".
- `/jobs/:id` **Job** — unified format, in this order: title, employer, labels (each
  with "Why?" disclosure showing the rule sentence); What you will do (duties); Where
  (address, small map, distance if known); Pay (amount + how it is paid, or "To be
  agreed"); When (shifts by day, hours per week, flexible or not); Contract; What you
  need (experience, qualifications, language as a task); Training; **Working
  conditions** — the 10 conditions + lifting as a table of rows with three clearly
  different states: "Yes"/"No" + "Employer says" or "Checked by an advisor on 12 Nov",
  and "Not known yet" + inline "Ask an advisor to check this"; never a single
  "accessible" badge. Then: At the event (date, venue, booth, "An advisor is there to
  help") when applicable; Source and "Last confirmed" date. Sticky action bar:
  **Apply**, **Ask an advisor for help**, Save, Listen.
- `/jobs/:id/apply` — one short form: how to reach me (phone call / text message /
  email — tiles) + value; when I can work (prefilled from profile); the job's one
  question, answered in my own words (VoiceInput); CV text only if `cv_required`;
  "Tell the employer what I need" — unchecked tiles from my profile needs, with "Nothing
  is shared unless you tick it"; "I would like to talk at the event" when applicable.
  Review step, then Send. Shows "3 of 5 open applications used".
- `/help` (optionally `?job=`) — what do you need help with (4 tiles), which conditions
  to check (when a job is given), message (VoiceInput), contact, explicit consent
  checkbox. Works without an account. Also says: "You can do the same by phone or at
  the Employment Espoo service point." (no invented phone numbers).
- `/applications` — each application as a card with a 3-step tracker
  (Sent → Interview → Answer), plain status line, the employer's note, days waiting,
  Withdraw; below, "My requests to an advisor" with status and the advisor's reply.
- `/saved` — saved jobs.
- `/profile` — sections with their own Edit: About me (name, contact, preferred way),
  Area I want to work in (district — "not your home address"), Kind of work, When I can
  work (grid + max hours), What I need at work ("Only you see this. You choose what to
  share each time you apply."), Languages, About me in my own words; Download my data;
  Delete my account (typed confirmation). First visit after sign-up shows the same
  sections as a skippable 4-step setup.
- `/sign-in`, `/sign-up` — large simple forms; sign-in shows a separated "Try a demo
  account" panel: Student (Aino), Retiree (Pekka), Job seeker with access needs
  (Amira), Employer (Sanna), City advisor (Leena).

### 5.5 Employer screens

- `/employer` — my jobs: status, positions, applications count, "Last confirmed", and a
  big **"Still open — confirm"** button per job (highlighted when older than 14 days),
  Close, Edit; "Add a job".
- `/employer/jobs/new`, `/employer/jobs/:id` — short stepped form, concrete questions:
  1 Title + kind of work; 2 What will the person do? (3–5 lines); 3 Where (address,
  district, pin on a small map — click to place; work mode); 4 Pay; 5 Days and hours
  (shift rows + hours per week + flexible); 6 Contract, experience, training;
  7 Language as a task; 8 Working conditions — each of the 10 as Yes / No / I don't
  know (default "I don't know") + lifting; 9 One question for applicants + is a CV
  really needed? (default No); 10 Preview exactly as residents see it, wording tips
  inline with "Use this wording" / "Keep mine", Publish or Save draft.
  "Prefer to tell an advisor? Send this to an advisor" → help request kind `other`.
- `/employer/applications` — by job: name, contact, availability, answer, needs the
  person chose to share ("Please arrange: …"), event wish; actions "Invite to an
  interview" (when/where required), "Offer the job", "Not this time" (short reason
  required). Shows how many days each person has waited.
- `/employer/company` — company profile + event booth info (read-only).

### 5.6 Advisor screens

- `/advisor` — queue of help requests (New / In progress / Done) with the person's
  message, contact and the job; actions: Take, Reply, Mark done; for `check_conditions`
  the unknown conditions are shown with Yes / No + note → saves as "Checked by an advisor".
- `/advisor/jobs` — the same map/list as residents ("browse together with a visitor"),
  plus Add job (same form, choose or add employer), Edit, and "Apply for someone" (the
  apply form with name/contact and a consent checkbox).
- `/advisor/follow-up` — applications waiting more than 7 days (with employer contact),
  stale jobs, counts by status, recent activity log.

## 6. Verification

Backend: `python -m pytest -q` — tests for labels, availability fit, each filter, auth
and ownership (401/403), application limit and duplicates, status changes with required
notes, job confirm/close, help request with and without account, advisor condition
check changing the job output, account deletion anonymisation, wording check, the
privacy tests in section 3, and the three seeded scenarios (Aino, Pekka, Amira) finding
their jobs through `GET /api/jobs` filters.
Frontend: `npm run build`, `npm run lint`. Then run the app and walk the three scenarios
end to end in a real browser if one is available, including 360px width at Extra-large text.
