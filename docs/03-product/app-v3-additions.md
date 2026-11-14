# App v3 additions — AI helpers, commute, paper notices, city support, Espoo languages, event mode

Builds on `app-v2-spec.md` (all its rules still hold: no scoring or ranking of people,
humans approve, synthetic data, minimal personal data). Owner-approved scope, 14 Nov.

Two files are already authored and must be used as they are (do not rewrite their
content): `app/api/prompts.py` (all LLM prompts) and `db/seed/support_programs.json`
(support programme facts with sources).

## 0. Configuration (`.env`, never committed; `.env.example` lists the names)

| Variable | Purpose | When missing |
|---|---|---|
| `NVIDIA_API_KEY` | Nemotron via `https://integrate.api.nvidia.com/v1` (OpenAI-compatible chat completions), model from `NVIDIA_MODEL`, default `nvidia/nemotron-3.5-super-vl-120b-a12b` | AI features report `enabled:false`; see each feature for the fallback |
| `DIGITRANSIT_API_KEY` | HSL routing, `POST https://api.digitransit.fi/routing/v2/hsl/gtfs/v1`, header `digitransit-subscription-key` | Commute time is hidden; straight-line distance stays |
| `PUBLIC_BASE_URL` | Base URL printed in QR codes | Frontend uses `window.location.origin` |

`GET /api/config` (public) → `{ai: bool, commute: bool}`. The UI never shows a control
that cannot work; where a feature is off for staff, show one plain line
("The AI assistant is not connected.").

`app/api/llm.py`: one small client (`requests`, 45 s timeout, one retry on 429/5xx with
backoff, temperature 0.1), a lenient JSON extractor, and `LLMUnavailable`. Tests inject a
fake client; no test calls the network. Every AI call writes an audit row
(`actor='ai'`, action, no personal data in `detail`).

## 1. Photo → job draft (employer and advisor)

- `POST /api/ai/job-draft` (employer or advisor) `{image_base64?, image_mime?
  ('image/jpeg'|'image/png'), text?}` — at least one of image/text; image ≤ 4 MB after
  the client downsizes it to max 1600 px. Sends `JOB_FROM_PHOTO_SYSTEM` + the image as an
  `image_url` data URL and/or the text. Returns `{draft, missing, wording_warnings,
  source_quotes}` validated against the job schema: unknown keys dropped, enums checked,
  invalid values turned into null and added to `missing`. **Nothing is saved.** 503 with
  a plain message when AI is off.
- UI: first step of the job form (employer and advisor) becomes "How do you want to
  start?" with three large tiles: **Take or upload a photo of a notice** (`<input
  type="file" accept="image/*" capture="environment">`), **Paste or dictate text**,
  **Fill in the form myself**. After a draft comes back the normal 10-step form opens
  pre-filled; every AI-filled field carries a small "From your photo — please check"
  mark with a disclosure showing the quoted source words, and every missing field is
  listed on the review step as "Not on the notice — still to fill or leave as not
  known". Wording warnings are shown as tips. The photo is not stored.
- Advisor shortcut on `/advisor/jobs`: "Add a job from a photo" (same flow, then choose
  or add the employer).

## 2. "Tell us what you are looking for" (public)

- `POST /api/ai/filters` (public, max 10 requests per minute per IP, text ≤ 600 chars)
  `{text, ui_language}` → `{filters, explanation, not_understood, source:'ai'|'rules'}`.
  With AI: `FILTERS_SYSTEM`; the result is validated against the whitelist of filter
  keys/values from the prompt (anything else is dropped into `not_understood`).
  Without AI (or on failure): a deterministic keyword parser
  (`app/api/rules/filter_words.py`) covering English and Finnish words for days, parts
  of day, "weekend", "part-time", "student", "retired/pension", "no experience",
  districts, fields of work, "remote", "near metro/train/station", "N hours" →
  `source:'rules'`.
- UI on `/`: above the quick filters, one field "Tell us what you are looking for" with
  VoiceInput and a "Find jobs" button, example text under it ("For example: two
  mornings a week near Matinkylä, no heavy lifting"). After the answer: the filters are
  applied to the URL, and a panel "This is what we set" lists each explanation with a
  remove button, plus "We could not set this: …" for `not_understood`. The person's
  text is not stored or logged.

## 3. "Show it simpler" and Espoo languages

Content languages (also the UI languages): `en`, `fi`, `sv`, `ru`, `ar`, `et`, `zh`,
`fa`, `sq`, `uk`.

- `POST /api/ai/simplify` (public, rate-limited as above) `{job_id, language}` →
  `{language, sections:{title, duties[], experience_note, qualifications[], onboarding,
  pay_note, lifting, apply_question, language_tasks[]}, machine: true}`. Uses
  `SIMPLIFY_SYSTEM`. **Only free-text fields go through the model.** Pay amount, hours,
  shifts, address, contract, conditions and dates are always rendered by the app from
  structured data with translated UI labels.
- Server-side checks before accepting a result: same keys; same list lengths; every
  digit sequence in the output also occurs in the input (reject otherwise). One retry,
  then 502 "We could not make a simpler version right now."
- Cache in `job_text_cache(job_id, language, source_hash, payload, created_at)`;
  invalidated when the job's text changes.
- UI on the job page: a button row "Show it simpler" + a language choice (native
  language names). The rewritten sections replace the originals inside a clearly marked
  block: "Simpler version written by a computer. The original text is the official
  one." with "Show the original". `dir="rtl"` and `lang` on the block for `ar`/`fa`.
  Listen reads the simpler version in that language when a voice exists.
- UI languages: add locale files for `sv`, `ru`, `ar`, `et`, `zh`, `fa`, `sq`, `uk`
  covering all resident-facing strings (jobs, job page, apply, help, applications,
  saved, profile, support page, event, sign-in/up, accessibility panel, shell).
  Employer and advisor screens may fall back to English in those languages. The
  language switch becomes a menu with native names. Whole-page RTL for `ar`/`fa`
  (`<html dir>`; check the top bar, filter row, job rows, forms, bottom nav).
  README must state that these locale files are machine-drafted and need native review.

## 4. Advisor helpers

- `POST /api/ai/advisor/questions` `{job_id}` (advisor) → `{opening, questions:
  [{field, question}], source}`. The list of unknown fields is computed by code
  (conditions without a row, null pay, null hours, empty shifts, empty onboarding, null
  lifting, language without task). With AI: `ADVISOR_QUESTIONS_SYSTEM`. Without AI: a
  fixed question per field from `app/api/rules/call_script.py`. UI: on a help request
  and on any job in `/advisor/jobs`, "Prepare a call to the employer" shows the script
  with the employer's contact, and next to each question the control to record the
  answer (Yes/No + note for conditions → `PUT /api/advisor/jobs/{id}/conditions`; a
  small field editor for the others → `PUT /api/jobs/{id}`). "Print call sheet".
- `POST /api/ai/advisor/note` `{text}` (advisor, AI required) → the object defined in
  `ADVISOR_NOTE_SYSTEM`, validated. UI: `/advisor` gets "New from a note": a textarea
  with VoiceInput ("Write or dictate what was said"), then a draft card of the detected
  type with editable fields, a job picker pre-filtered by `job_hint`, the `left_out`
  list, and a required checkbox "The person agreed that I record and send this" before
  Save. Save calls the existing endpoints (`/api/help-requests`,
  `/api/advisor/applications`, `/api/advisor/jobs/{id}/conditions`). The note text is
  not stored.

## 5. Commute by public transport and "near a station"

- Stations: `db/seed/stations.json` — metro and railway stations in and next to Espoo
  (name, mode `metro`|`train`, lat, lon), fetched once from OpenStreetMap via the
  Overpass API by `scripts/fetch_stations.py` (attribution "© OpenStreetMap
  contributors" in the file meta and README). Every job output gets
  `nearest_station: {name, mode, distance_m} | null` (straight line, on-site/hybrid jobs
  only) and the derived label `near_station` when `distance_m ≤ 800`
  ("Near a station", why: "About 450 m from Matinkylä metro station, in a straight
  line."). New filter `near_station=1` and quick-filter chip.
- `GET /api/commute?job_id=&district=` (public; 503 when no key) → `{minutes, walk_m,
  transfers, legs:[{mode, route, from, to, minutes}], arrive_by, date, source:'HSL'}`.
  Origin = district centre from the catalogue; destination = job coordinates; arrive by
  the start of the job's first shift on the next such weekday (jobs without shifts:
  next weekday 09:00). Uses the `planConnection` query; take the fastest itinerary.
  Cache in `commute_cache(job_id, district, payload, computed_at)` for 7 days.
- `GET /api/jobs` accepts `commute_max` (minutes, needs `district`): uses the cache,
  computes missing ones with at most 5 parallel calls; jobs whose commute cannot be
  computed are kept and marked `commute: null`.
- UI: once a person has chosen an area (filter or profile), each on-site job row and the
  job page show "About 24 min by bus and metro from Matinkylä (arriving by 18:00)" with
  a disclosure listing the legs; otherwise the straight-line distance. Without a key,
  only distance and the station line are shown. Never ask for a home address.
- Verify against the live API only if `DIGITRANSIT_API_KEY` is present; otherwise unit
  tests with a recorded-shape fake response, and say so in the report.

## 6. Paper notice with QR

- Add `qrcode@1.5.4`. Route `/jobs/:id/print` (public): an A4 print layout (CSS `@page
  A4`, black on white, no navigation): title in very large serif; employer; the facts as
  big rows (What you will do — max 4 duties; Where; Pay; When; Contract; "No experience
  needed" when true; up to 4 confirmed "yes" working conditions with their source); a
  large QR code linking to the job page with the caption "Scan to read more and apply";
  the line "No smartphone? Ask at an Employment Espoo service point."; "Last confirmed
  <date>"; and a bottom row of 8 tear-off strips, each with the job title, a small QR
  and the short URL, rotated for cutting. "Print" button hidden in print.
- Entry points: "Print a paper notice" on the job page (everyone), on each job in the
  employer's list and in `/advisor/jobs`. Printing uses the current UI language and, if
  a simpler version is being shown, that version.

## 7. City support — for employers and for job seekers

Data: `db/seed/support_programs.json`, served by `GET /api/support` (public).

- **Employer**: on the job form review step and on each job in `/employer`, a panel
  "City support that may fit this job" lists the programmes whose `job_rule` matches
  the job (evaluate the tiny rule language in code: `always`, `contract in (...)`,
  `hours_min >= N`, `hours_max >= N`, joined by `and`; unknown hours → not matched),
  each with name, amount, the `for_employer` text, source link, and "checked on" date,
  under the disclaimer. Button "Ask an advisor to call me about this" → help request
  with new kind `employer_support` (add to schema, API, advisor queue). **Never shown
  per applicant, and applications never carry any eligibility flag.**
- **Job seeker**: new page `/support` ("Support you may get", linked from the job page,
  the profile and the footer). Step 1: "Which of these fit you? Tick any — nothing is
  saved or sent." with the `situations` as large checkbox tiles. Step 2: cards for
  programmes where all `resident_when_all` are ticked and (no `resident_when_any` or at
  least one ticked) and `for_resident` is not null: name, amount in large type, the
  text, "Money goes to: you / the employer", source link, then "Ask an advisor to
  confirm this" → `/help` with the programme named in the message. All matching is done
  in the browser; the ticks are kept in component state only (not localStorage, not
  sent). Listen button on each card.
- On the job page (resident view), one quiet line when the job matches at least one
  employer-side programme: "The city may support an employer who hires for this job.
  See support you may get." → `/support`.
- Advisor: `/advisor/support` shows the whole catalogue as a reference table.

## 8. Event mode

Purpose: connect the map to the City's recruitment event and make sure every booth
conversation gets an answer.

Schema: `event_visitor(user_id, event_id, code UNIQUE per event — 4 digits)`,
`event_plan(user_id, event_id, employer_id, added_at)`,
`event_talk(id, event_id, user_id, employer_id, status CHECK IN
('talked','answered'), outcome CHECK IN ('next_step','not_now') NULL, employer_note,
talked_at, answered_at)`. `employer_event.booth` values like `A1`…`C4`.

- Resident `/event`: event name, date, venue, "An advisor is at the event to help";
  a **schematic booth plan** (CSS grid by booth code, labelled "Not to scale") and the
  equivalent list of employers with booth and their open jobs; "Add to my plan" per
  employer (sign-in required). "My plan": ordered by booth, with the person's 4-digit
  **visitor number** in very large type and the sentence "When you say this number at a
  booth, that employer sees your name and how to reach you." "Print my plan" (A4 with
  the number, booths and one line per employer).
- Employer `/employer/event`: booth; "People planning to visit you: N" (a number only,
  no names); "Record a conversation": enter a visitor number → creates `event_talk`
  and shows the person's name and preferred contact; list of conversations each
  needing an answer ("Next step" / "Not now" + a required short note). 404 with a plain
  message for an unknown number; a number can be recorded once per employer.
- Resident `/applications` gets a section "Conversations at the event" with the same
  tracker and the employer's note. Advisor `/advisor/follow-up` lists conversations
  without an answer for more than 7 days, with employer contact.
- `GET /api/event` gains booths and jobs; new endpoints: `GET/PUT/DELETE
  /api/me/event-plan[/{employer_id}]`, `GET /api/employer/event`,
  `POST /api/employer/event/talks {code}`, `POST /api/employer/event/talks/{id}/answer`.
- Seed: Aino has a plan with 3 employers; Sanna's café has 2 recorded conversations
  (one answered). Nav: "Event" replaces nothing — add it as the 5th item on wide
  screens and inside the Menu on phones (bottom bar stays 4 items).

## 9. Tests and verification

pytest additions: job-draft validation (bad enum → null + missing; protected-ground
phrases only in warnings; nothing saved); filters whitelist + rules fallback for the
three demo sentences (student evenings/weekends, retiree two mornings near Matinkylä,
step-free + seated); simplify checks (changed number rejected, list length mismatch
rejected, cache hit, invalidation); call-script fallback covers every unknown field;
advisor note validation and that diagnoses in `left_out` are not persisted; rate limit;
`near_station` label and filter; commute with a fake Digitransit client + cache +
`commute_max`; support rule evaluation and that no application/employer response
contains programme ids or situation flags; event plan, visitor code, talk recording
(unknown code, duplicate), answer required note, name hidden before a talk; `/api/config`.
Frontend: `npm run build`, `npm run lint`; browser screenshots of every new screen.
